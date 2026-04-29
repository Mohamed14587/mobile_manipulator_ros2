// تعريف الدبابيس (Pins)
const int IN1 = 6;    // التحكم في الاتجاه 1
const int IN2 = 7;    // التحكم في الاتجاه 2
const int ENA = 9;    // التحكم في السرعة (يجب أن يكون دبوس PWM)

void setup() {
  // إعداد الدبابيس كمخرجات
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);

  // إعداد التواصل التسلسلي
  Serial.begin(115200);
  Serial.setTimeout(1);
  
  Serial.println("DC Motor Controller Ready. Send speed (-255 to 255):");
}

void loop() {
  if (Serial.available()) {
    // قراءة السرعة المطلوبة من السيريال
    int speed = Serial.readString().toInt();
    
    controlDCMotor(speed);
  }
}

// دالة التحكم في المحرك
void controlDCMotor(int speed) {
  if (speed > 0) {
    // حركة للأمام
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, speed); // تحويل الرقم لسرعة (PWM)
  } 
  else if (speed < 0) {
    // حركة للخلف
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, abs(speed)); // استخدام القيمة المطلقة للسرعة
  } 
  else {
    // توقف
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 0);
  }
}