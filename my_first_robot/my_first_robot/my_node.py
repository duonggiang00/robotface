import rclpy 
from rclpy.node import Node

class MyFirstNode(Node):
    def __init__(self):
        super().__init__('my_first_node')
        self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info('Hello World')

def main(args=None):
    rclpy.init(args=args) 
    node = MyFirstNode()
    rclpy.spin(node)

    rclpy.shutdown()

if __name__ == '__main__':
    main()