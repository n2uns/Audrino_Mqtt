/*
  SimpleMQTTClient.ino
  The purpose of this exemple is to illustrate a simple handling of MQTT and Wifi connection.
  Once it connects successfully to a Wifi network and a MQTT broker, it subscribe to a topic and send a message to it.
  It will also send a message delayed 5 seconds later.
*/

#include "EspMQTTClient.h"

const int Analogin = 36;
const int DigIn = 23;
const int Digout = 16;
const int Bultinled = 2;
char Device[] = "mydevice";


EspMQTTClient client(
  "espdevices",
  "Kevin8386",
  "192.168.18.185",  // MQTT Broker server ip
  "admin",   // Can be omitted if not needed
  "kevin8386",   // Can be omitted if not needed
  Device,     // Client name that uniquely identify your device
  1884              // The MQTT port, default to 1883. this line can be omitted
);

void setup()
{

Serial.begin(115200);

  // Optional functionalities of EspMQTTClient
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overridded with enableHTTPWebUpdater("user", "password").
  client.enableOTA(); // Enable OTA (Over The Air) updates. Password defaults to MQTTPassword. Port is the default OTA port. Can be overridden with enableOTA("password", port).
 
  //client.enableLastWillMessage( toCharArray(mesg) , "I am going offline");  // You can activate the retain flag by setting the third parameter to true
  pinMode (Digout, OUTPUT);
  pinMode (DigIn, INPUT);
 
 }

// This function is called once everything is connected (Wifi and MQTT)
// WARNING : YOU MUST IMPLEMENT IT IF YOU USE EspMQTTClient
void onConnectionEstablished()
{
   IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
 // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe("cmd", [](const String & payload) {
    Serial.println("fron cmd" + payload);
 // if 
    digitalWrite( Bultinled, payload.toInt() );
  //  digitalWrite( Bultinled, HIGH );
  });

  // Subscribe to "mytopic/wildcardtest/#" and display received message to Serial
  client.subscribe("status", [](const String & topic, const String & payload) {
    Serial.println("(From status) topic: " + topic + ", payload: " + payload);
    digitalWrite( Digout, payload.toInt() );
  });

  // Publish a message to "mytopic/test"
  //client.publish("mytopic/test", "This is a message"); // You can activate the retain flag by setting the third parameter to true

  // Execute delayed instructions
 // client.executeDelayed(5 * 1000, []() {
 //   client.publish("mytopic/wildcardtest/test123", "This is a message sent 5 seconds later");
 // });
}

void loop()
{
 String mesg;
 mesg = Device;
 int me;
  client.loop();
  me = me++;
  delay(5000);
  // Execute delayed instructions
 
  client.publish(mesg + "/status", String( analogRead( Analogin )));
  client.publish(mesg + "/cmd", String( digitalRead( Digout )));

}
