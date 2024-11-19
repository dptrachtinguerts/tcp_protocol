import cv2
import numpy as np

class RadarExtractor:
    def __init__(self, radar_radius, radar_center, shape, remove_north=True, northmark_px_len=49):
        self.radar_radius = radar_radius
        self.radar_center = radar_center

        self.shape = shape

        self.mask = np.zeros(shape, dtype=np.uint8)
        if remove_north:
            cv2.circle(self.mask, radar_center, radar_radius - northmark_px_len, 255, -1)
        else:
            cv2.circle(self.mask, radar_center, radar_radius, 255, -1)

    def radar_from_tpn_recording(self, frame):
        # mask radar sweep from frame
        radar_isolated = cv2.bitwise_and(frame, frame, mask=self.mask)

        # crop frame
        radar_isolated = radar_isolated[self.radar_center[1] - self.radar_radius : self.radar_center[1] + self.radar_radius,
                                        self.radar_center[0] - self.radar_radius : self.radar_center[0] + self.radar_radius]
        
        # binary mask on every obstacle pixel
        obstacles_signature = cv2.inRange(radar_isolated, np.array([158, 127, 170]), np.array([248, 255, 255]))
        
        # rebuild frame for display
        radar_img = cv2.bitwise_and(radar_isolated, radar_isolated, mask=obstacles_signature)
        
        return obstacles_signature, radar_img