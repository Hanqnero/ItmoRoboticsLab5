import math

from vec2 import Vec2
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B
from regulator import PRegulator, Regulator
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
                 logger: Logger = None):

        self.robot_init_time = time()

        self.position = position
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.linear_regulator = linear_regulator
        self.angular_regulator = angular_regulator
        self.wheel_radius = wheel_radius
        self.base_length = base_length
        self.dt = dt
        self.logger = logger

        self.x_odometry = Integral(position.x, 0, dt)
        self.y_odometry = Integral(position.y, 0, dt)
        self.alpha_odometry = Integral(position.alpha, 0, dt)

        # Set up motors
        self.left_motor.run_direct()
        self.right_motor.run_direct()
        self.left_motor.duty_cycle_sp = 0
        self.right_motor.duty_cycle_sp = 0

    def goto(self, target: Vec2, allowed_linear_error: float) -> None:
        goto_start_time = time()
        cycle_start_time = time()
        cycle_end_time = time()

        print("Executing goto: (x={:.3f}, y={:.3f}) ...".format(target.x, target.y))

        while (self.position - target).norm() < allowed_linear_error:
            # Update position. Odometry in Cartesian coordinates
            # --------------------------------------------------
            error_vector = target - self.position
            angular_error = target.alpha - self.position.alpha

            left_wheel_speed = self.left_motor.speed / 180 * math.pi
            right_wheel_speed = self.right_motor.speed / 180 * math.pi

            linear_speed = (left_wheel_speed + right_wheel_speed) * self.wheel_radius / 2
            angular_speed = (right_wheel_speed - left_wheel_speed) * self.wheel_radius / self.base_length

            x_speed = linear_speed * math.cos(self.position.alpha)
            y_speed = angular_speed * math.sin(self.position.alpha)

            self.x_odometry.add_measure(x_speed)
            self.y_odometry.add_measure(y_speed)
            self.alpha_odometry.add_measure(angular_speed)

            # Update motors current
            # ---------------------
            linear_component_current = self.linear_regulator(error_vector.norm())
            angular_component_current = self.angular_regulator(angular_error)

            self.left_motor.duty_cycle_sp = linear_component_current - angular_component_current
            self.right_motor.duty_cycle_sp = linear_component_current + angular_component_current

            # Cycle end. Update time variables and log here
            # ---------------------------------------------
            if isinstance(self.logger, Logger):
                self.logger.log(
                    {'t': time() - self.robot_init_time, 'x': self.position.x, 'y': self.position.y}
                )

            cycle_start_time = cycle_end_time
            cycle_end_time = time()
            cycle_time = cycle_end_time - cycle_start_time
            if cycle_time > self.dt:
                print("WARNING: Actual cycle time exceeded given fixed cycle time")

            # In case of noticeable difference between expected and actual time, wait
            elif self.dt - cycle_time > 0.005:
                # Эмпирическим путем получил что фактическое время сна
                # на четверть больше указанного при мелких t
                sleep(abs(self.dt - cycle_time)*.75)
        else:
            # Stop motors after loop
            self.left_motor.duty_cycle_sp = 0
            self.right_motor.duty_cycle_sp = 0

            print("goto (x={:.3f}, y={:.3f}) completed. Actual position is (x={:.3f}, y={:.3f})".format(
               target.x, target.y, self.position, self.position
            ))


if __name__ == '__main__':
    logger = Logger
    robot = Robot(
        position=Vec2(0, 0),
        left_motor=LargeMotor(OUTPUT_A),
        right_motor=LargeMotor(OUTPUT_B),
        linear_regulator=PRegulator(kp=10),
        angular_regulator=PRegulator(kp=10),

        wheel_radius=0.055,
        base_length=0.18,
        dt=0.03
    )
    robot.goto(Vec2(0, 0), 0.10)
    robot.goto(Vec2(1,0), 0.10)
    robot.goto(Vec2(1,1,), 0.10)
    robot.goto(Vec2(0, 1), 0.10)
    robot.goto(Vec2(0,0), 0.10)
