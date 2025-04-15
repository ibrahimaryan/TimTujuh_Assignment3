from machine import Pin, ADC, PWM
import time
import urequests as requests
import dht
import network

# Inisialisasi sensor dan komponen
ldr = ADC(Pin(35))  # LDR di GPIO35
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_10BIT)

dht_pin = Pin(15)  # DHT11 di GPIO15
sensor_dht = dht.DHT11(dht_pin)

pir = Pin(4, Pin.IN)  # PIR di GPIO5

# Inisialisasi buzzer di GPIO21
buzzer = PWM(Pin(21), duty=0)  # Mulai dengan duty 0 (diam)

# Konfigurasi Wi-Fi
SSID = "Redmi9"
PASSWORD = "haaaaaah"

# Konfigurasi Ubidots
TOKEN = "BBUS-A33lRaUTEicWD2INjCihT8n0yODbOp"
DEVICE_LABEL = "esp32-sic6-assignment3"
VARIABLE_LABEL_TEMP = "Temperature"
VARIABLE_LABEL_HUM = "Humidity"
VARIABLE_LABEL_LDR = "LDR"
VARIABLE_LABEL_MOTION = "Motion"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("[INFO] Menghubungkan ke Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("[INFO] Terhubung ke Wi-Fi:", wlan.ifconfig())
    else:
        print("[ERROR] Gagal terhubung ke Wi-Fi!")

def read_sensors():
    try:
        sensor_dht.measure()
        temperature = sensor_dht.temperature()
        humidity = sensor_dht.humidity()
        ldr_value = ldr.read()
    except Exception as e:
        print("[ERROR] Gagal membaca sensor DHT11:", e)
        temperature, humidity, ldr_value = None, None, None

    motion = pir.value()
    
    return temperature, humidity, motion, ldr_value

def build_payload(temperature, humidity, motion, ldr_value):
    if temperature is None or humidity is None:
        print("[ERROR] Data sensor tidak valid, tidak mengirim data!")
        return None

    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "ldr": ldr_value,
        "motion": motion
    }

    # Cek kondisi potensi kebakaran
    if temperature > 26 and humidity < 90 and ldr_value > 200:
        payload["alert"] = "Ada potensi kebakaran"
        buzzer.freq(1000)
        buzzer.duty(512)  # Bunyikan buzzer
        print("[ALERT] Potensi kebakaran terdeteksi!")
    else:
        buzzer.duty(0)  # Matikan buzzer jika tidak memenuhi
    return payload

def post_request(payload):
    if payload is None:
        return False

    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    attempts = 0
    status = 400
    while status >= 400 and attempts < 5:
        try:
            print(f"[DEBUG] Mengirim data ke {url}, Percobaan {attempts+1}")
            req = requests.post(url, headers=headers, json=payload)
            status = req.status_code
            print(f"[DEBUG] Response Status: {status}")
            print(f"[DEBUG] Response Body: {req.text}")

            if status < 400:
                print("[INFO] Data berhasil dikirim ke Ubidots:", req.json())
                return True
            else:
                print(f"[WARNING] Gagal mengirim ke Ubidots, kode status: {status}")
        except Exception as e:
            print("[ERROR] Gagal mengirim ke Ubidots:", str(e))

        attempts += 1
        time.sleep(1)

    print("[ERROR] Gagal mengirim data ke Ubidots setelah 5 kali percobaan.")
    return False

def post_db(payload):
    SERVER_URL = "http://192.168.79.213:5000/sensor"

    if payload is None:
        print("[ERROR] Payload tidak valid, tidak mengirim data!")
        return False

    headers = {"Content-Type": "application/json"}

    print("[DEBUG] Data yang dikirim ke server:", payload)

    try:
        response = requests.post(SERVER_URL, json=payload, headers=headers)
        print("[INFO] Respon Server:", response.text)
        response.close()
        return True
    except Exception as e:
        print("[ERROR] Gagal mengirim data:", str(e))
        return False

def main():
    temperature, humidity, motion, ldr_value = read_sensors()
    payload = build_payload(temperature, humidity, motion, ldr_value)

    if payload:
        print("[INFO] Mengirim data ke Ubidots dan MongoDB...")
        post_request(payload)
        post_db(payload)

if __name__ == '__main__':
    connect_wifi()
    while True:
        main()
        time.sleep(8)