#include <Servo.h>

Servo motor;

void setup() {
  // توصيل محرك السيرفو بالدبوس رقم 8
  motor.attach(8);
  // ضبط المحرك على زاوية البداية (90 درجة - المنتصف)
  motor.write(90);

  // إعداد التواصل التسلسلي بنفس السرعة المستخدمة في عقدة ROS
  Serial.begin(115200);
  Serial.setTimeout(1);
}

void loop() {
  // التحقق من وصول بيانات من الحاسوب
  if (Serial.available()) {
    // قراءة النص (الزاوية) وتحويله إلى رقم
    int angle = Serial.readString().toInt();
    
    // التأكد من أن الزاوية في النطاق المسموح به (0-180)
    if (angle >= 0 && angle <= 180) {
      motor.write(angle);
    }
  }
  
  // تأخير بسيط لاستقرار المعالج
  delay(10); 
}