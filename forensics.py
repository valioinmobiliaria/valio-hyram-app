"""
Módulo de Protección Forense, Esteganografía Unicode y Sellos Criptográficos.
Desarrollado para Grupo VALIO S.A.S. — HyRAM+ Web
"""

import hashlib
import json
from datetime import datetime

# Secuencia base para esteganografía Unicode (Zero-Width Characters)
# Invisibles en la visualización gráfica o de texto normal, pero persistentes en la memoria y stream de bytes.
ZW_CHARS = {
    '0': '\u200B',  # Zero-width space
    '1': '\u200C',  # Zero-width non-joiner
    '2': '\u200D',  # Zero-width joiner
    '3': '\uFEFF',  # Zero-width no-break space (BOM)
}

REVERSE_ZW = {v: k for k, v in ZW_CHARS.items()}

VALIO_LEGAL_IDENTITY = "VALIO S.A.S. | NIT 901.810.123-5 | Seguridad de Procesos & PPAM | www.grupovalio.com"
VALIO_SALT = "VALIO_PROCESS_SAFETY_SECURE_SALT_2026_HYRAM_ENGINE"

def text_to_zero_width(secret_text: str) -> str:
    """Codifica una cadena de texto en una secuencia invisible de caracteres Unicode de ancho cero."""
    encoded_chars = []
    for char in secret_text:
        # Convertir a 4 dígitos en base 4 (0-255 en 4 dígitos de 2 bits)
        val = ord(char)
        base4_str = f"{(val >> 6) & 3}{(val >> 4) & 3}{(val >> 2) & 3}{val & 3}"
        for digit in base4_str:
            encoded_chars.append(ZW_CHARS[digit])
    return "".join(encoded_chars)

def zero_width_to_text(zw_text: str) -> str:
    """Decodifica una secuencia de caracteres de ancho cero a su texto original."""
    digits = [REVERSE_ZW[c] for c in zw_text if c in REVERSE_ZW]
    chars = []
    for i in range(0, len(digits), 4):
        chunk = digits[i:i+4]
        if len(chunk) == 4:
            val = (int(chunk[0]) << 6) | (int(chunk[1]) << 4) | (int(chunk[2]) << 2) | int(chunk[3])
            chars.append(chr(val))
    return "".join(chars)

def get_forensic_watermark_token() -> str:
    """Genera un token esteganográfico invisible de autoría corporativa VALIO."""
    secret_payload = f"GRUPO_VALIO_PROPRIETARY_INTEGRATION_2026_SANDIA_GPL3_COMPLIANT_{datetime.utcnow().strftime('%Y%m')}"
    return text_to_zero_width(secret_payload)

def generate_tamper_seal(input_params: dict, results_summary: dict) -> dict:
    """
    Genera un identificador único de verificación y un hash SHA-256 a prueba de manipulaciones.
    Permite validar la autenticidad e integridad de cualquier cálculo emitido por la plataforma.
    """
    serialized_data = json.dumps({
        "inputs": input_params,
        "summary": results_summary,
        "corp": VALIO_LEGAL_IDENTITY,
        "salt": VALIO_SALT
    }, sort_keys=True)
    
    full_sha = hashlib.sha256(serialized_data.encode('utf-8')).hexdigest().upper()
    certificate_id = f"VAL-HYR-{datetime.utcnow().strftime('%Y%m%d')}-{full_sha[:8]}"
    
    return {
        "certificate_id": certificate_id,
        "sha256": full_sha,
        "timestamp_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "forensic_token": get_forensic_watermark_token(),
        "issuer": "Grupo VALIO S.A.S. - División de Seguridad de Procesos"
    }
