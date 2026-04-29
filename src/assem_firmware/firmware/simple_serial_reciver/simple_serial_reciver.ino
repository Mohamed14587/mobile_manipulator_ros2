#define LED_PIN 13

void setup() {
  // إعداد دبوس الـ LED كمخرج
  pinMode(LED_PIN, OUTPUT);
  // التأكد من إطفاء الـ LED في البداية
  digitalWrite(LED_PIN, LOW);

  // بدء التواصل التسلسلي بسرعة 115200
  Serial.begin(115200);
  // تحديد وقت انتظار قراءة البيانات بـ 1 مللي ثانية
  Serial.setTimeout(1);
}

void loop() {
  // التحقق من وجود بيانات واردة عبر المنفذ التسلسلي
  if (Serial.available()) {
    // قراءة النص الوارد وتحويله إلى رقم صحيح
    int x = Serial.readString().toInt();

    if (x == 0) {
      digitalWrite(LED_PIN, LOW);  // إطفاء الـ LED إذا كانت القيمة 0
    } 
    else {
      digitalWrite(LED_PIN, HIGH); // تشغيل الـ LED لأي قيمة أخرى
    }
  }
  
  // تأخير بسيط جداً (ملاحظة: دالة delay تأخذ أرقاماً صحيحة بالمللي ثانية)
  delay(1); 
}
