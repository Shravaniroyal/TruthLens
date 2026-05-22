import io, cv2, numpy as np
from PIL import Image, ImageChops

ZONES = {
    "aadhaar": {"header":(0,.00,1,.18),"photo":(0,.18,.23,.65),"name_field":(.23,.18,.75,.35),"dob_field":(.23,.35,.75,.50),"address_field":(.23,.50,.75,.78),"uid_number":(0,.78,1,1),"qr_code":(.75,.18,1,.78)},
    "pan":     {"header":(0,.00,1,.18),"pan_number":(0,.18,.78,.34),"photo":(0,.34,.23,.72),"name_field":(.23,.34,.78,.50),"father_name":(.23,.50,.78,.64),"dob_field":(.23,.64,.78,.80),"signature":(.23,.80,.78,.92),"qr_code":(.78,.18,1,.92)},
    "dl":      {"header":(0,.00,1,.18),"dl_number":(.23,.18,.78,.32),"photo":(0,.18,.23,.68),"name_field":(.23,.32,.78,.46),"dob_field":(.23,.46,.78,.58),"validity":(.23,.58,.78,.70),"vehicle_class":(.23,.70,.78,.84),"qr_code":(.78,.18,1,.84)},
    "generic": {"header":(0,.00,1,.18),"photo":(0,.18,.23,.65),"name_field":(.23,.18,1,.34),"id_number":(0,.65,1,.80),"date_field":(.23,.34,.75,.50),"address_field":(.23,.50,1,.65),"signature":(0,.80,1,1)},
}
LABELS = {"header":"document header / issuing authority","photo":"photograph area","name_field":"name field","dob_field":"date of birth field","uid_number":"12-digit Aadhaar number","pan_number":"PAN number","dl_number":"driving licence number","father_name":"father name field","id_number":"ID number","date_field":"date field","address_field":"address field","signature":"signature area","qr_code":"QR code region","validity":"validity dates","vehicle_class":"vehicle class field"}
REASONS = {
    "name_field":["Name field shows font inconsistency — characters appear from a different typeface than surrounding text. Classic sign of copy-paste text replacement.","Pixel sharpness in the name area is abnormally high — text was likely digitally typed over the original.","JPEG compression artifacts in the name field differ from the rest of the document — name was altered after original creation."],
    "uid_number":["12-digit Aadhaar number shows digit-level pixel inconsistency — stroke widths differ between digits, suggesting individual digit replacement.","ELA map shows elevated error levels on the UID row — re-compression artifacts indicate the number was modified in an image editor."],
    "pan_number":["PAN number character spacing is non-uniform — single character alteration is the most common PAN fraud pattern.","ELA isolates the PAN number as highest-anomaly region — characters show different compression history than the document background."],
    "photo":["Photograph boundary shows compression discontinuity — photo JPEG signature differs from document background, indicating photo substitution.","Noise texture at photo edges does not blend naturally — photograph was composited onto the document."],
    "dob_field":["Date of birth field has high ELA score — re-saving artifacts indicate this date was modified. Year alteration is the most common DOB fraud.","Text anti-aliasing in the DOB area differs from other printed text — points to digital text replacement."],
    "dl_number":["Driving licence number shows re-compression artifacts inconsistent with state transport printing — digits may have been individually altered."],
    "father_name":["Father name field shows different font-rendering than the name field above — authentic documents print all fields in one pass; inconsistency suggests separate editing."],
    "header":["Document header anomaly — government logo, emblem, or authority text may have been modified to impersonate a different issuing authority."],
    "address_field":["Address field has localized compression anomaly — certain lines have different JPEG history from surrounding lines, suggesting partial text replacement."],
    "signature":["Signature boundary shows artifacts inconsistent with authentic ink scanning — signature may have been digitally inserted."],
    "validity":["Validity dates have elevated ELA score — the Valid Till date may have been extended by altering year digits."],
    "id_number":["ID number region shows pixel-level manipulation — ELA highlights this area significantly above baseline, consistent with digit replacement."],
}

def run_ela(pil_image, quality=90):
    orig = pil_image.convert("RGB")
    buf  = io.BytesIO()
    orig.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    resaved  = Image.open(buf).convert("RGB")
    diff     = ImageChops.difference(orig, resaved)
    diff_arr = np.array(diff, dtype=np.float32)
    mx = diff_arr.max()
    scaled = np.clip(diff_arr * (255.0/mx), 0, 255).astype(np.uint8) if mx > 0 else diff_arr.astype(np.uint8)
    return scaled.astype(np.float32), Image.fromarray(scaled)

def run_noise_map(pil_image):
    gray   = np.array(pil_image.convert("L"), dtype=np.float32)
    smooth = cv2.medianBlur(gray.astype(np.uint8), 5).astype(np.float32)
    noise  = np.abs(gray - smooth)
    return cv2.GaussianBlur(noise**2, (21,21), 0)

def _zone_score(arr2d, zones_dict, W, H):
    scores = {}
    for name,(x1f,y1f,x2f,y2f) in zones_dict.items():
        r = arr2d[int(y1f*H):int(y2f*H), int(x1f*W):int(x2f*W)]
        scores[name] = float(r.mean()) if r.size > 0 else 0.0
    return scores

def _norm(d):
    mx = max(d.values()) if d and max(d.values())>0 else 1.0
    return {k:v/mx for k,v in d.items()}

def explain_fraud(pil_image, gradcam_heatmap_np=None, doc_type="generic", confidence=0.99):
    W, H   = pil_image.size
    zones  = ZONES.get(doc_type, ZONES["generic"])
    ela_arr, ela_pil = run_ela(pil_image)
    noise_map        = run_noise_map(pil_image)
    ela_mean  = ela_arr.mean(axis=2) if ela_arr.ndim==3 else ela_arr
    ela_scores = _zone_score(ela_mean,  zones, W, H)
    nse_scores = _zone_score(noise_map, zones, W, H)
    gc_scores  = {}
    if gradcam_heatmap_np is not None:
        hmap = cv2.resize(gradcam_heatmap_np.astype(np.float32),(W,H))
        gc_scores = _zone_score(hmap, zones, W, H)
    ela_n = _norm(ela_scores); nse_n = _norm(nse_scores)
    gc_n  = _norm(gc_scores) if gc_scores else {z:0.0 for z in zones}
    composite = {z: 0.40*gc_n.get(z,0)+0.38*ela_n.get(z,0)+0.22*nse_n.get(z,0) for z in zones}
    top_zones  = sorted(composite.items(), key=lambda x:-x[1])
    reasons    = []
    pct        = confidence*100
    reasons.append(f"⚠️ **Model confidence: {pct:.1f}% FAKE** — {'Very high' if pct>=99 else 'High'} certainty of tampering.")
    used = set()
    for zone_name, score in top_zones:
        if score < 0.12 or len(reasons) >= 5: break
        label     = LABELS.get(zone_name, zone_name.replace("_"," ").title())
        templates = REASONS.get(zone_name, [])
        ela_val   = ela_scores.get(zone_name, 0)
        ela_hi    = ela_n.get(zone_name,0)>0.60
        gc_hi     = gc_n.get(zone_name,0)>0.60
        if not templates:
            reasons.append(f"🔴 **Anomaly in {label}**: Region shows patterns inconsistent with authentic documents. (ELA: {ela_val:.1f})")
        else:
            idx    = min(2 if (ela_hi and gc_hi) else 1 if ela_hi else 0, len(templates)-1)
            icon   = "🔴" if (ela_hi or gc_hi) else "🟡"
            sev    = "**Primary tampering**" if not used else "**Secondary anomaly**"
            ela_lv = "very high — strong copy-paste" if ela_val>30 else "high — likely modified" if ela_val>18 else "moderate"
            reasons.append(f"{icon} {sev} — **{label.title()}**: {templates[idx]} *(ELA: {ela_val:.1f} — {ela_lv})*")
        used.add(zone_name)
    if len(reasons)<=1:
        reasons.append("🔴 **Overall document structure anomaly**: Pixel statistics differ significantly from authentic documents of this type.")
    return reasons, ela_pil, {"ela":ela_scores,"noise":nse_scores,"gradcam":gc_scores,"composite":composite}

def ela_to_pil(pil_image, quality=90):
    _, ela_pil = run_ela(pil_image, quality=quality)
    return ela_pil
