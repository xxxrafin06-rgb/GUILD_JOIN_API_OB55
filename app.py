from flask import Flask, request, jsonify
import requests
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import encode_id_clan_pb2
import data_pb2
import reqClan_pb2
import jwt
import json
import base64
from urllib.parse import urlparse, parse_qs
from google.protobuf import json_format
from google.protobuf import descriptor_pool, symbol_database, runtime_version
from google.protobuf.internal import builder
from google.protobuf.message import Message

RELEASE_VERSION = "OB55"
CLIENT_VERSION = "1.132.1"
CLIENT_VERSION_CODE = "2019121229"
MAJORLOGIN = "https://loginbp.ppmainecoonghj.com"

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
if hasattr(app, 'json'):
    app.json.sort_keys = False

DEV_CREDITS = {
    "DEVELOPER": "MAHIN CODEX",
    "TELEGRAM": "@CODEX_007",
    "TelegramChannel": "@FF_FILE_ZONE"
}

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")
MAIN_IV = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")
USERAGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"

HTTP_LIMITS = httpx.Limits(max_keepalive_connections=20, max_connections=50)
HTTP_TIMEOUT = httpx.Timeout(15.0, connect=5.0)
_http_client = httpx.Client(limits=HTTP_LIMITS, timeout=HTTP_TIMEOUT, verify=False)

api_endpoints = {
    "IND": "https://client.ind.freefiremobile.com",
    "AMERICAS": "https://client.us.freefiremobile.com", 
    "DEFAULT": "https://clientbp.ggpolarbear.com"
}

runtime_version.ValidateProtobufRuntimeVersion(runtime_version.Domain.PUBLIC, 6, 30, 0, "", "FreeFire.proto")
_sym_db = symbol_database.Default()
DESCRIPTOR = descriptor_pool.Default().AddSerializedFile(
    b'\n\x0e\x46reeFire.proto"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t'
    b'\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d '
    b'\x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t"]\n\x10\x42lacklist'
    b'InfoRes\x12\x1e\n\nban_reason\x18\x01 \x01(\x0e\x32\n.BanReason\x12\x17\n'
    b'\x0f\x65xpire_duration\x18\x02 \x01(\r\x12\x10\n\x08\x62\x61n_time\x18\x03 '
    b'\x01(\r"f\n\x0eLoginQueueInfo\x12\r\n\x05\x61llow\x18\x01 \x01(\x08\x12'
    b'\x16\n\x0equeue_position\x18\x02 \x01(\r\x12\x16\n\x0eneed_wait_secs\x18'
    b'\x03 \x01(\r\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08"\xa0\x03\n\x08'
    b'LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region'
    b'\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_'
    b'region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t'
    b'\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\x19\n\x11recommend_'
    b'regions\x18\x07 \x03(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl'
    b'\x18\t \x01(\r\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mul'
    b'ator_score\x18\x0b \x01(\r\x12$\n\tblacklist\x18\x0c \x01(\x0b\x32\x11.'
    b'BlacklistInfoRes\x12#\n\nqueue_info\x18\r \x01(\x0b\x32\x0f.LoginQueue'
    b'Info\x12\x0e\n\x06tp_url\x18\x0e \x01(\t\x12\x15\n\rapp_server_id\x18'
    b'\x0f \x01(\r\x12\x0f\n\x07\x61no_url\x18\x10 \x01(\t\x12\x0f\n\x07ip_city'
    b'\x18\x11 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x12 \x01(\t*\xa8\x01\n'
    b'\tBanReason\x12\x16\n\x12\x42\x41N_REASON_UNKNOWN\x10\x00\x12\x1b\n\x17'
    b'\x42\x41N_REASON_IN_GAME_AUTO\x10\x01\x12\x15\n\x11\x42\x41N_REASON_'
    b'REFUND\x10\x02\x12\x15\n\x11\x42\x41N_REASON_OTHERS\x10\x03\x12\x16\n'
    b'\x12\x42\x41N_REASON_SKINMOD\x10\x04\x12 \n\x1b\x42\x41N_REASON_IN_GAME'
    b'_AUTO_NEW\x10\xf6\x07\x62\x06proto3'
)
_globals = globals()
builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "FreeFire_pb2", _globals)
LoginReq = _globals["LoginReq"]
LoginRes = _globals["LoginRes"]

def custom_pad(text: bytes) -> bytes:
    padding_length = AES.block_size - (len(text) % AES.block_size)
    return text + bytes([padding_length] * padding_length)

def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv).encrypt(custom_pad(plaintext))

def json_to_proto(json_data: str, proto_message: Message) -> bytes:
    json_format.ParseDict(json.loads(json_data), proto_message)
    return proto_message.SerializeToString()

def try_parse_login_res(data: bytes):
    try:
        msg = LoginRes()
        msg.ParseFromString(data)
        if msg.account_id and msg.account_id > 0:
            return json.loads(json_format.MessageToJson(msg))
    except Exception:
        pass
    return None

def extract_login_res(raw: bytes) -> dict:
    parsed = try_parse_login_res(raw)
    if parsed: return parsed
    idx = 0
    while True:
        idx = raw.find(b"\x08", idx)
        if idx == -1: break
        parsed = try_parse_login_res(raw[idx:])
        if parsed: return parsed
        idx += 1
    jwt_marker = raw.find(b"eyJhbGciOiJIUzI1NiIs")
    if jwt_marker != -1:
        for i in range(jwt_marker - 1, max(jwt_marker - 300, -1), -1):
            if raw[i] == 0x42:
                parsed = try_parse_login_res(raw[i:])
                if parsed: return parsed
                break
    raise Exception("Could not parse LoginRes.")

def major_login_new(access_token, open_id):
    try:
        body = json.dumps({
            "open_id": open_id,
            "open_id_type": "4",
            "login_token": access_token,
            "orign_platform_type": "4",
        })
        proto_bytes = json_to_proto(body, LoginReq())
        payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)

        headers = {
            "User-Agent": USERAGENT,
            "Accept": "*/*",
            "Accept-Encoding": "deflate, gzip",
            "X-Ga-Sv": "1789534056",
            "Authorization": "Bearer",
            "X-Ga": "v1 1",
            "Releaseversion": RELEASE_VERSION,
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "2018.4.11f1",
            "PlAy_VeR": CLIENT_VERSION,
            "Ob_VeR": RELEASE_VERSION,
        }
        resp = _http_client.post(f"{MAJORLOGIN}/MajorLogin", data=payload, headers=headers)
        msg = extract_login_res(resp.content)
        if msg and "token" in msg:
            return {"token": msg["token"]}, None
        return None, "MajorLogin failed"
    except Exception as e:
        return None, f"MajorLogin error: {str(e)}"

def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = account + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    headers = {
        "User-Agent": USERAGENT,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = _http_client.post(url, data=payload, headers=headers)
    data = resp.json()
    return data.get("access_token", "0"), data.get("open_id", "0")

def generate_jwt_from_credentials(uid: str, password: str):
    token_val, open_id = get_access_token(f"uid={uid}&password={password}")
    if token_val == "0" or open_id == "0":
        return None
    login_result, error = major_login_new(token_val, open_id)
    if login_result:
        return login_result['token']
    return None

def get_jwt_token_from_credentials(uid, password):
    if uid and password:
        jwt_token = generate_jwt_from_credentials(uid, password)
        if jwt_token:
            return jwt_token, None
    return None, "Invalid or missing uid and password"

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(plain_text, AES.block_size)).hex()

def get_region_from_jwt(jwt_token):
    try:
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        lock_region = decoded.get('lock_region', 'IND')
        if lock_region and isinstance(lock_region, str):
            return lock_region.upper()
        return 'IND'
    except Exception:
        return 'IND'

def get_region_type(region):
    region = region.upper()
    if region == "IND":
        return "IND"
    elif region in ["BR", "US", "NA", "SAC"]:
        return "AMERICAS"
    else:
        return "DEFAULT"

def create_clan_payload(clan_id):
    try:
        message = reqClan_pb2.MyMessage()
        message.field_1 = int(clan_id)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        encrypted_data = cipher.encrypt(pad(message.SerializeToString(), AES.block_size))
        return encrypted_data, None
    except Exception as e:
        return None, f"Payload creation failed: {str(e)}"

def make_clan_request(jwt_token, clan_id, endpoint):
    try:
        region = get_region_from_jwt(jwt_token)
        region_type = get_region_type(region)
        base_url = api_endpoints.get(region_type, api_endpoints["DEFAULT"])
        
        encrypted_data, payload_error = create_clan_payload(clan_id)
        if payload_error:
            return None, payload_error, None
        
        url = f"{base_url}/{endpoint}"
        
        headers = {
            "Expect": "100-continue",
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": RELEASE_VERSION,
            "Content-Type": "application/octet-stream",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; ASUS_Z01QD Build/RP1A.200720.012)",
            "Host": base_url.replace("https://", ""),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        response = requests.post(url, headers=headers, data=encrypted_data, timeout=30)
        
        try:
            resp_info = data_pb2.response()
            resp_info.ParseFromString(response.content)
            
            result = {}
            fields = ['id', 'special_code', 'status_code', 'error_code']
            for field in fields:
                if hasattr(resp_info, field):
                    value = getattr(resp_info, field)
                    if value is not None and value != 0 and value != "":
                        result[field] = value
            return response, None, result
        except Exception:
            try:
                decoded_text = response.content.decode('utf-8', errors='ignore').strip()
                return response, None, {'raw_text': decoded_text}
            except Exception:
                return response, None, {'raw_hex': response.content.hex()}
    except Exception as e:
        return None, f"Network error: {str(e)}", None

def get_guild_name_with_token(guild_id, jwt_token):
    try:
        base_url = api_endpoints.get(get_region_type(get_region_from_jwt(jwt_token)), api_endpoints["DEFAULT"])
        my_data = encode_id_clan_pb2.MyData()
        my_data.field1 = int(guild_id)
        my_data.field2 = 1

        encrypted_hex = encrypt_api(my_data.SerializeToString().hex())
        url = base_url + "/GetClanInfoByClanID"
        
        headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; ASUS_Z01QD Build/PI)',
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'Authorization': f'Bearer {jwt_token}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': RELEASE_VERSION,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_hex), timeout=8)
        if response.status_code == 200:
            msg = data_pb2.response()
            msg.ParseFromString(response.content)
            return getattr(msg, "special_code", "Unknown")
        return "Unknown"
    except Exception:
        return "Unknown"

@app.route("/", methods=["GET"])
def root_route():
    return jsonify({
        **DEV_CREDITS,
        "Project": "Free Fire Guild Management API",
        "Message": "Welcome to Free Fire Guild Join API",
        "API_Usage_Guide": {
            "API_Format": {
                "Join_Guild": "/join?guild_id={id}&uid={uid}&password={password}"
            },
            "Examples": {
                "Example_1": "/join?guild_id=3000000001&uid=guest_123&password=pass"
            }
        }
    })

@app.route("/join", methods=["GET"])
def join_guild_route():
    try:
        guild_id = request.args.get("guild_id")
        uid = request.args.get("uid")
        password = request.args.get("password")
        
        if not guild_id:
            return jsonify({
                **DEV_CREDITS,
                "success": False,
                "error": "guild_id is required"
            }), 400
        
        try:
            guild_id = int(guild_id)
        except ValueError:
            return jsonify({
                **DEV_CREDITS,
                "success": False,
                "error": "guild_id must be a valid number"
            }), 400
        
        jwt_token, error = get_jwt_token_from_credentials(uid, password)
        if error:
            return jsonify({
                **DEV_CREDITS,
                "success": False,
                "error": f"Authentication failed: {error}"
            }), 400
        
        region = get_region_from_jwt(jwt_token)
        guild_name = get_guild_name_with_token(guild_id, jwt_token)
        
        response, error, raw_response = make_clan_request(jwt_token, guild_id, "RequestJoinClan")
        
        if error:
            return jsonify({
                **DEV_CREDITS,
                "success": False,
                "error": error,
                "message": f"Failed to join guild: {error}",
                "guild_id": guild_id,
                "guild_name": guild_name,
                "region": region,
                "http_status": response.status_code if response else None,
                "raw_response": raw_response
            }), 400
        
        return jsonify({
            **DEV_CREDITS,
            "success": True,
            "message": "Guild join request sent successfully",
            "guild_id": guild_id,
            "guild_name": guild_name,
            "region": region,
            "status_code": response.status_code if response else 200,
            "raw_response": raw_response
        })
        
    except Exception as e:
        return jsonify({
            **DEV_CREDITS,
            "success": False,
            "error": f"Join request failed: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5001)