# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       user                                                         #
# 	Created:      15/11/2024, 15:54:02                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
#region VEXcode Generated Robot Configuration
from vex import *

# Brain should be defined by default
brain=Brain()

# Robot configuration code
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, True)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b)
right_motor_a = Motor(Ports.PORT9, GearSetting.RATIO_18_1, False)
right_motor_b = Motor(Ports.PORT10, GearSetting.RATIO_18_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b)
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 319.19, 295, 40, MM, 0.5)
#drivetrain.set_drive_velocity(50, PERCENT)

# AI Classification Competition Element IDs
class GameElements:
    MOBILE_GOAL = 0
    RED_RING = 1
    BLUE_RING = 2

# AI Vision Color Descriptions
AiVis_COLOR1 = Colordesc(1, 36, 155, 238, 10, 0.2) #azul
AiVis_COLOR2 = Colordesc(3, 200, 212, 23, 10, 0.2) #verde
AiVis_COLOR3 = Colordesc(2, 219, 50, 107, 10, 0.2) #rojo
# AI Vision Code Descriptions
AiVis = AiVision(Ports.PORT5, AiVis_COLOR1, AiVis_COLOR2, AiVis_COLOR3, AiVision.ALL_AIOBJS)
AiVis.model_detection(True)

optical = Optical(Ports.PORT20)

motor_hook = Motor(Ports.PORT11, GearSetting.RATIO_36_1, False)
motor_threadmill = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)

dist = Distance(Ports.PORT4)
#dist_b = Distance(Ports.PORT6)


# wait for rotation sensor to fully initialize
wait(30, MSEC)

# ---------- GENERALS ---------- #

is_there_a_goal = False
hook_activated = False
goal_detected = False

# ---------- AIVision Objects ---------- #
def activate_hook():

    global hook_activated
    motor_hook.spin_to_position(50, DEGREES)
    hook_activated = True

def desactivate_hook():

    global hook_activated, goal_detected

    motor_hook.spin_to_position(0, DEGREES)
    hook_activated = False

def goal_eval():
    global is_there_a_goal
    hue = optical.hue()

    # Solo procesa el valor si no es None y está dentro del rango esperado
    if hue is not None:
        if 90 < hue < 150:
            is_there_a_goal = not is_there_a_goal


def detecting_goal():
    global goal_detected

    # Inicializamos la bandera
    goal_centered = False

    while not goal_detected:
        
        brain.screen.print("Buscando Objetivo.")
        brain.screen.new_line()
            
        # Detectar objetos con AiVision
        detected_objects = AiVis.take_snapshot(AiVision.ALL_AIOBJS)

        # Inicializar variables para el objeto más grande
        largest_goal = None
        largest_area = 0

        # Iterar sobre los objetos detectados
        for obj in detected_objects:
            if obj.id == GameElements.MOBILE_GOAL:
                area = obj.width * obj.height
                if area > largest_area:
                    largest_area = area
                    largest_goal = obj

        # Si se encuentra el objetivo más grande
        if largest_goal:
            brain.screen.print("objetivo más grande.")
            brain.screen.new_line()
            goal_center_x = largest_goal.centerX
            brain.screen.print("center_x = ",goal_center_x)
            brain.screen.new_line()

            # Verificar si el objetivo está centrado
            if 160 < goal_center_x < 240:
                brain.screen.print("Objetivo centrado.")
                brain.screen.new_line()
                goal_centered = True
                goal_detected = True
            elif goal_center_x < 160:
                brain.screen.print("LEFT")
                brain.screen.new_line()
                drivetrain.turn_for(LEFT, 10, DEGREES)
            elif goal_center_x > 240:
                brain.screen.print("RIGHT")
                brain.screen.new_line()
                drivetrain.turn_for(RIGHT, 10, DEGREES)
        else:
            brain.screen.print("Buscando objeto...")
            brain.screen.new_line()
            drivetrain.turn_for(RIGHT, 15, DEGREES)
        
        wait(100,MSEC)
            
        # if goal_centered:
        #                 # Si el objetivo está centrado, usar únicamente el sensor de distancia
        #     dist_g = dist.object_distance(MM)
        #     brain.screen.clear_screen()
        #     brain.screen.print("Distancia:", dist_g)
        #     brain.screen.new_line()

        #     if dist_g > 400:
        #         drivetrain.drive(FORWARD)
        #     else:
        #         brain.screen.print("Distancia alcanzada, girando 180 grados.")
        #         brain.screen.new_line()
        #         drivetrain.turn_for(RIGHT, 180, DEGREES)
        #         goal_eval()
        #         if is_there_a_goal:
        #             drivetrain.drive_for(REVERSE, 300, MM)
        #             brain.screen.print("Hook activado...")
        #             brain.screen.new_line()
        #             activate_hook()
        #             drivetrain.stop()
        #             goal_detected = False


def detect_rings():

    # Inicializamos la bandera
    ring_centered = False

    while True:
        if not ring_centered:
            # Detectar objetos con AiVision
            detected_objects = AiVis.take_snapshot(AiVision.ALL_AIOBJS)

            # Inicializar variables para el objeto más grande
            largest_ring = None
            largest_area = 0

            # Iterar sobre los objetos detectados
            for obj in detected_objects:
                if obj.id == GameElements.BLUE_RING:
                    area = obj.width * obj.height
                    if area > largest_area:
                        largest_area = area
                        largest_ring = obj

            # Si se encuentra el objetivo más grande
            if largest_ring:
                # Obtener la posición del objeto
                ringX = largest_ring.centerX

                # Lógica para centrar el anillo
                if ringX < 240:
                    drivetrain.turn_for(RIGHT, 10, DEGREES)
                else:
                    ring_centered = True
                    brain.screen.print("Anillo centrado.")
                    brain.screen.new_line()
                    drivetrain.drive(FORWARD)
            else:
                # Si no hay anillo, busca girando
                brain.screen.print("Buscando anillo...")
                brain.screen.new_line()
                drivetrain.turn_for(RIGHT, 30, DEGREES)

    wait(10, MSEC)


def starting_threadmill():
    motor_threadmill.spin(REVERSE, 80, PERCENT)

# Función principal
def main():
    global hook_activated, goal_detected

    while True:  # Mantener el programa corriendo en un loop continuo
        brain.screen.clear_screen()
        brain.screen.set_cursor(1, 1)

        if hook_activated:
            brain.screen.print("Buscando Donas...")
            brain.screen.new_line()
            starting_threadmill()
            detect_rings()

            # Ejemplo: Desactivar hook después de procesar las donas (condición personalizada)
            # hook_activated = False  # O alguna lógica para decidir cuándo desactivar el gancho.

        else:
            detecting_goal()

        # Añadir un pequeño retraso para evitar ciclos muy rápidos
        wait(100, MSEC)



if __name__ == "__main__":
    main()