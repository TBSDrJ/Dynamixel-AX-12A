from ax12a import AX_12A

motor1 = AX_12A(id = 1)
motor2 = AX_12A(id = 2)
AX_12A.connectAll()
motor1.wheelMode();
motor2.wheelMode();
motor1.setMovingSpeed(300);
motor2.setMovingSpeed(300);
