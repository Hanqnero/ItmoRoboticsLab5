import math

from vec2 import Vec2, shift_angle
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B
from regulator import Regulator, clamp
from odometry import Integral
from time import time, sleep
from logger import Logger


class Robot:
    def __init__(self,
                 position: Vec2,
                 left_motor: LargeMotor,
                 right_motor: LargeMotor,
                 linear_regulator: Regulator,
                 angular_regulator: Regulator,
                 wheel_radius: float,
                 base_length: float,
                 dt: float,
                 ):

        self.robot_init_time = time()

        self.position = position
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.linear_regulator = linear_regulator
        self.angular_regulator = angular_regulator
        self.wheel_radius = wheel_radius
        self.base_length = base_length
        self.dt = dt
        self.my_logger = Logger()

        self.x_odometry = Integral(position.x, 0, dt)
        self.y_odometry = Integral(position.y, 0, dt)
        self.alpha_odometry = Integral(position.alpha, 0, dt)

        # Set up motors
        self.left_motor.run_direct()
        self.right_motor.run_direct()
        self.left_motor.duty_cycle_sp = 0
        self.right_motor.duty_cycle_sp = 0

        # Write robot parameters to log
        self.my_logger.write_dict({
                'linear_kp': self.linear_regulator.kp,
                'angular_kp': self.angular_regulator.kp,
                'wheel_radius': self.wheel_radius,
                'base_length': self.base_length,
            })

    def update_position(self):
        # Update position. Odometry in Cartesian coordinates
        # --------------------------------------------------

        left_wheel_speed = math.radians(self.left_motor.speed)
        right_wheel_speed = math.radians(self.right_motor.speed)

        linear_speed = (left_wheel_speed + right_wheel_speed) * self.wheel_radius / 2
        angular_speed = (right_wheel_speed - left_wheel_speed) * self.wheel_radius / self.base_length

        x_speed = linear_speed * math.cos(self.position.alpha)
        y_speed = linear_speed * math.sin(self.position.alpha)

        self.x_odometry.add_measure(x_speed)
        self.y_odometry.add_measure(y_speed)
        self.alpha_odometry.add_measure(angular_speed)

        self.position.x = self.x_odometry.value
        self.position.y = self.y_odometry.value
        self.position.alpha = self.alpha_odometry.value

    def goto(self, target: Vec2, allowed_linear_error: float) -> None:

        goto_start_time = time()
        flag = False

        print("Executing goto: (x={:.3f}, y={:.3f}) ...".format(target.x, target.y))

        error_vector = target - self.position

        cycle_start_time = time()
        while error_vector.norm() > allowed_linear_error and not flag:

            self.update_position()

            error_vector = target - self.position

            angular_error = shift_angle(error_vector.alpha - self.position.alpha)

            # Update motors current
            # ---------------------
            linear_component_current = self.linear_regulator(error_vector.norm())
            angular_component_current = self.angular_regulator(angular_error)

            left_motor_out = clamp(linear_component_current - angular_component_current, 100, -100)
            right_motor_out = clamp(linear_component_current + angular_component_current, 100, -100)

            self.left_motor.run_direct(duty_cycle_sp=left_motor_out)
            self.right_motor.run_direct(duty_cycle_sp=right_motor_out)

            # Cycle end. Update time variables and log here
            # ---------------------------------------------
            self.my_logger.log(
                {
                    't': time()-self.robot_init_time,
                    'x': self.position.x,
                    'y': self.position.y,
                    'alpha': self.position.alpha,
                    'error_x': error_vector.x,
                    'error_y': error_vector.y,
                    'angular_error': angular_error,
                    'speed_left': left_motor_out,
                    'speed_right': right_motor_out
                }
            )

            cycle_end_time = time()
            cycle_time = cycle_end_time - cycle_start_time
            cycle_start_time = cycle_end_time

            if time() - goto_start_time > 15:
                print("Maximum time of 15sec for goto exceeded. Current position (x={:.3f}, y={:.3f})"
                      .format(self.position.x, self.position.y))
                flag = True
                break

            if cycle_time > self.dt:
                print("WARNING: Actual cycle time exceeded given fixed cycle time by {:.4f}".format(cycle_time-self.dt))
            # In case of noticeable difference between expected and actual time, wait
            if cycle_time - self.dt > 0.005:
                # Эмпирическим путем получил что фактическое время сна
                # на четверть больше указанного при мелких t
                sleep(abs(self.dt - cycle_time) * .75)
        else:
            print("goto (x={:.3f}, y={:.3f}) completed. Actual position (x={:.3f}, y={:.3f}), distance {:.3f}".format(
                target.x, target.y, self.position.x, self.position.y, error_vector.norm()))
        # Stop motors after loop
        self.left_motor.stop()
        self.right_motor.stop()

        sleep(300)

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()
        self.my_logger.close()
        exit(0)


if __name__ == '__main__':
    logger = Logger
    robot = Robot(
        position=Vec2(0, 0),
        left_motor=LargeMotor(OUTPUT_B),
        right_motor=LargeMotor(OUTPUT_A),
        linear_regulator=Regulator(300, saturation=100, dt=0.06),
        angular_regulator=Regulator(200 / math.pi * 2, saturation=200, dt=0.06),

        wheel_radius=0.026,
        base_length=0.17,
        dt=0.06
    )
    robot.position.alpha = 0

    try:
        robot.goto(Vec2(0, 2), 0.02)
        robot.goto(Vec2(2, 2), 0.02)
        robot.goto(Vec2(2, 0), 0.02)
        robot.goto(Vec2(0, 0), 0.02)
        robot.stop()
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        robot.stop()
