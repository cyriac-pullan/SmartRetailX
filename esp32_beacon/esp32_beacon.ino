#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// ==========================================
// CONFIGURATION
// ==========================================
// Define the name of the beacon based on its aisle location.
// You MUST change this for each of your 4 ESP32 devices to match the backend expectation:
// ESP32 1: "ESP32_AISLE_1"
// ESP32 2: "ESP32_AISLE_2"
// ESP32 3: "ESP32_AISLE_3"
// ESP32 4: "ESP32_AISLE_4"
#define BEACON_NAME "ESP32_AISLE_4"

// Optional: Set transmit power. Higher power = higher range, but you need to 
// recalibrate the backend if you change this.
#define TX_POWER ESP_PWR_LVL_P9

void setup() {
  Serial.begin(115200);
  Serial.println("Starting SmartMart BLE Beacon...");

  // 1. Initialize the BLE device with the expected name
  BLEDevice::init(BEACON_NAME);

  // 2. Set the transmit power. 
  // P9 is max power (+9 dBm) which gives good stable signals for RSSI tracking
  BLEDevice::setPower(TX_POWER); 

  // 3. Create the BLE Server
  BLEServer *pServer = BLEDevice::createServer();

  // 4. Create the BLE Advertising object
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  
  // Configure advertising data
  // We add a generic placeholder Service UUID. 
  // The backend Python script filters by device.name, not UUID, so this is just filler.
  pAdvertising->addServiceUUID("12345678-1234-5678-1234-56789abcdef0");
  
  // True so active scanners (like Bleak in python) can request the full device name
  pAdvertising->setScanResponse(true);
  
  // Recommended advertising intervals for iOS/Android compatibility
  pAdvertising->setMinPreferred(0x06);  
  pAdvertising->setMinPreferred(0x12);

  // 5. Start advertising
  BLEDevice::startAdvertising();
  
  Serial.print("BLE Beacon Active! Broadcasting as: ");
  Serial.println(BEACON_NAME);
}

void loop() {
  // Beacons only need to advertise in the background, which runs automatically.
  // We can just sleep to save power/CPU.
  delay(5000);
}
