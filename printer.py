import json
import ssl
import sys
import time
import ftplib
from pathlib import Path
import paho.mqtt.client as mqtt
import config

MQTT_PORT = 8883
FTP_PORT = 990
CACHE_DIR = "cache"


def _ftp_upload(gcode_path: str) -> str:
    """Upload G-code to the printer's cache directory via FTPS. Returns remote filename."""
    local = Path(gcode_path)
    remote_name = local.name

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # Bambu uses self-signed cert

    # Port 990 uses implicit FTPS — SSL must wrap the socket before the
    # welcome message, which ftplib.FTP_TLS doesn't do by default.
    class ImplicitFTP_TLS(ftplib.FTP_TLS):
        def connect(self, host, port=990, timeout=30):
            self.host = host
            self.port = port
            self.timeout = timeout
            self.sock = self.context.wrap_socket(
                ftplib.socket.create_connection((host, port), timeout),
                server_hostname=host,
            )
            self.af = self.sock.family
            self.file = self.sock.makefile("r", encoding=self.encoding)
            self.welcome = self.getresp()
            return self.welcome

    ftp = ImplicitFTP_TLS(context=ctx)
    ftp.connect(config.BAMBU_IP, FTP_PORT)
    ftp.login("bblp", config.BAMBU_ACCESS_CODE)
    ftp.prot_p()

    try:
        ftp.cwd(CACHE_DIR)
        with open(local, "rb") as f:
            try:
                ftp.storbinary(f"STOR {remote_name}", f)
            except TimeoutError:
                # Bambu doesn't send TLS close_notify — upload succeeded anyway
                pass
    finally:
        try:
            ftp.quit()
        except Exception:
            pass

    print(f"    Uploaded {local.name} to printer cache")
    return remote_name


def _build_print_command(remote_filename: str, subtask_name: str = "ai_print") -> dict:
    return {
        "print": {
            "command": "project_file",
            "param": "Metadata/plate_1.gcode",
            "url": f"file:///sdcard/{CACHE_DIR}/{remote_filename}",
            "plate_idx": 0,
            "subtask_name": subtask_name,
            "bed_type": "auto",
            "timelapse": False,
            "bed_leveling": True,
            "flow_cali": False,
            "vibration_cali": True,
            "layer_inspect": False,
            "use_ams": False,
        },
        "user_id": "0",
        "sequence_id": str(int(time.time())),
    }


def upload_and_print(gcode_path: str):
    """Upload G-code to printer and trigger the print via MQTT."""
    remote_name = _ftp_upload(gcode_path)

    command = _build_print_command(remote_name)
    topic_request = f"device/{config.BAMBU_SERIAL}/request"

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set("bblp", config.BAMBU_ACCESS_CODE)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    client.connect(config.BAMBU_IP, MQTT_PORT, keepalive=60)
    client.loop_start()

    time.sleep(1)  # allow connection to establish
    result = client.publish(topic_request, json.dumps(command), qos=1)
    result.wait_for_publish(timeout=5)

    client.loop_stop()
    client.disconnect()

    print(f"    Print command sent")


def poll_until_complete():
    """Subscribe to the printer's report topic and print status until the print finishes."""
    topic_report = f"device/{config.BAMBU_SERIAL}/report"
    done_states = {"FINISH", "FAILED"}
    state = {"value": "UNKNOWN"}

    def on_connect(client, userdata, flags, reason_code, properties):
        client.subscribe(topic_report, qos=0)

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload)
            print_data = data.get("print", {})
            gcode_state = print_data.get("gcode_state")
            percent = print_data.get("mc_percent")
            remaining = print_data.get("mc_remaining_time")

            if gcode_state:
                state["value"] = gcode_state
                parts = [f"State: {gcode_state}"]
                if percent is not None:
                    parts.append(f"{percent}%")
                if remaining is not None:
                    parts.append(f"{remaining}min remaining")
                print(f"    [{' | '.join(parts)}]")

            if gcode_state in done_states:
                client.disconnect()
        except (json.JSONDecodeError, KeyError):
            pass

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set("bblp", config.BAMBU_ACCESS_CODE)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config.BAMBU_IP, MQTT_PORT, keepalive=60)
    print("    Monitoring print status (Ctrl+C to stop watching)...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()

    final = state["value"]
    if final == "FINISH":
        print("\nPrint complete!")
    elif final == "FAILED":
        print("\nPrint failed.")
    else:
        print(f"\nStopped watching. Last known state: {final}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python printer.py <path/to/file.gcode>")
        sys.exit(1)

    gcode_path = sys.argv[1]
    print(f"Uploading {gcode_path} and starting print...")
    upload_and_print(gcode_path)
    poll_until_complete()
