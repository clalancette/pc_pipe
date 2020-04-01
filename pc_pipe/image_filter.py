#!/usr/bin/env python3
import sys
import time

import posix_ipc

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class MockImageFilter(Node):

    def __init__(self):
        super().__init__('image_filter')
        self.sub = self.create_subscription(Image, 'image_raw', self.image_callback, 10)
        self.pub = self.create_publisher(Image, 'image_filtered', 10)

    def image_callback(self, msg):
        #self.get_logger().info(f'Message received [{msg.header.stamp}]')
        now_ms = int(time.time() * 1000)
        self.get_logger().info("{} received message at {} ms".format(self.get_name().upper(), now_ms))

        sem = posix_ipc.Semaphore('/pc_pipe_sem', flags=posix_ipc.O_CREAT, initial_value=1)
        sem.acquire()
        with open('/tmp/pc_pipe_times.csv', 'a') as outfp:
            outfp.write('"%s SUB", %d\n' % (self.get_name().upper(), now_ms))
        sem.release()
        sem.close()

        self.pub.publish(msg)



def main(args=None):
    rclpy.init(args=args)
    node = MockImageFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main(sys.argv)
