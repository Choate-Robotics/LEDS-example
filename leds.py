from wpilib import AddressableLED, PowerDistribution
import math

class Type():
        
        def KStatic(r: int, g: int, b: int):
            ''' Returns a static color type'''
            return {
                'type': 1,
                'color': {
                    'r': r,
                    'g': g,
                    'b': b
                }
            }
        
        def KRainbow():
            return {
                'type': 2
            }
        
        def KTrack(r1: int, g1: int, b1:int, r2:int, g2:int, b2:int):
            return {
                'type': 3,
                'color': {
                    'r1': r1,
                    'g1': g1,
                    'b1': b1,
                    'r2': r2,
                    'g2': g2,
                    'b2': b2
                }
            }
        
        def KBlink(r:int,g:int,b:int):
            return {
                'type': 4,
                'color': {
                    'r': r,
                    'g': g,
                    'b': b
                }
            }
            
        def KLadder(typeA,typeB,percent: float,speed: int):
            ''' Returns a ladder type (typeA is the bottom, typeB is the top. They are both Type objects)'''
            return {
                'type': 5,
                'percent': percent, # 0-1
                'typeA': typeA, # Instance of Type class
                'typeB': typeB, # Instance of Type class
                'speed': speed
            }
        

        
class ADLeds():
    ''' Wrapper class for the Addressable LEDS from PWM RIO'''
    m_led: AddressableLED
    
    
    def __init__(self, id: int, size: int):
        self.size = size
        self.id = id
        self.speed = 5
        self.track_index = 0
        self.blink_index = 0
        self.active_mode = None
        self.last_active_mode = None
        self.last_brightness = None
        self.last_speed = None
        
    def init(self):
        ''' Initializes and starts the LEDS'''
        self.m_rainbowFirstPixelHue = 0
        self.m_led = AddressableLED(self.id)
        self.m_led.setLength(self.size)
        self.m_ledBuffer = self.m_led.LEDData()
        self.array = [self.m_ledBuffer for i in range(self.size)]
        self.m_led.setData(self.array)
        self.m_led.start()
        
        
    def enable(self):
        ''' Enables the LEDS'''
        self.m_led.start()
    
    def disable(self):
        ''' Disables the LEDS'''
        self.m_led.stop()
        
        
    def getArray(self):
        ''' Returns an array of LEDData'''
        return [self.m_led.LEDData() for i in range(self.size)].copy()
    
    def getCurrentCycle(self):
        ''' Returns the current LEDData array'''
        return self.array
    
    def getCurrentType(self):
        ''' Returns the current LEDData type setting'''
        return self.active_mode
        
        
    def storeCurrent(self):
        ''' Stores the current LEDData array and type setting to the history'''
        self.last_active_mode = self.active_mode
        self.last_speed = self.speed
    
    def setLED(self, type: Type, brightness: float = 1.0, speed: int = 5):
        ''' Sets the LEDData array and type setting'''
        self.storeCurrent()
        self.active_mode = type
        self.speed = speed
        
    def getLED(self):
        ''' Returns the LEDData array and type setting'''
        if self.active_mode == None:
            return {
                'type': 0,
                'color': {
                    'r': 0,
                    'g': 0,
                    'b': 0
                }
            }
        else:
            return self.active_mode
        
    def setLast(self):
        ''' Sets the LEDData array and type setting to the last stored'''
        self.active_mode = self.last_active_mode
        self.speed = self.last_speed
        self.brightness = self.last_brightness
        
    def match(self, type: Type):
        
        ''' Matches the LEDData array to the type setting'''
        
        res = self.getArray()
        match type['type']:
            case 1:
                color = type['color']
                res = self._setStatic(color['r'], color['g'], color['b'])
            case 2:
                res = self._setRainbow()
            case 3:
                color = type['color']
                res = self._setTrack(color['r1'], color['g1'], color['b1'], color['r2'], color['g2'], color['b2'])
            case 4:
                color = type['color']
                res = self._setBlink(color['r'], color['g'], color['b']) 
            case 5:
                percent = type['percent']
                res = self._setLadder(type['typeA'], type['typeB'], percent, type['speed'])
            case _:
                res = self._setRainbow()
        
        return res
                
    def cycle(self):  
        '''
        cycles through LED array
        this should be called periodically
        '''
        self.array = self.match(self.active_mode)
        
        # self.m_led.setData(self.match(self.active_mode))
        
        self.m_led.setData(self.array)
        
    def _setStatic(self, red: int, green: int, blue: int):
        
        ''' Sets the LEDData array to a static color'''
        
        static = self.getArray()
        
        for i in range(self.size):
            static[i].setRGB(red, green, blue)
        # self.m_led.setData(self.array)
        
        return static
        
    def _setRainbow(self):
        
        ''' Sets the LEDData array to a rainbow'''
        # arr = [self.m_led.LEDData() for i in range(self.size)]
        arr = self.getArray()
        for i in range(self.size):
            # Calculate the hue - hue is easier for rainbows because the color
            # shape is a circle so only one value needs to precess
            hue = math.floor(self.m_rainbowFirstPixelHue + (i * 180 / self.size) % 180)
            # Set the value
            arr[i].setHSV(hue, 255, 128)
    
        # Increase by to make the rainbow "move"
        self.m_rainbowFirstPixelHue += self.speed
        # Check bounds
        self.m_rainbowFirstPixelHue %= 180
        # self.m_led.setData(self.array)
        
        return arr.copy()
        
    def _setTrack(self, r1, g1, b1, r2, g2, b2):
        
        ''' Sets the LEDData array to a track'''
        
        track = self.getArray()
        for i in range(self.size):
            track[i].setRGB(r1, g1, b1)
            
        for i in range(self.track_index, self.size, 4):
            track[i].setRGB(r2, g2, b2)
        
        self.track_index += 1
        
        if self.track_index > self.size: 
            self.track_index = 0
            
        return track
        
        # self.m_led.setData(self.array)
        
    def _setBlink(self, r,g,b):
        
        ''' Sets the LEDData array to blink'''
        
        blink = self.getArray()
        if self.blink_index / (2 * self.speed) <= .5:
            for i in range(self.size):
                blink[i].setRGB(r,g,b)
        else:
            for i in range(self.size):
                blink[i].setRGB(0,0,0)
        
        self.blink_index += 1
        if self.blink_index > 2 * self.speed:
            self.blink_index = 0  
            
        return blink
            
    def _setLadder(self, typeA: Type, typeB: Type, percent: float, speed: int):
        
        ''' Sets the LEDData array to a ladder'''
        
        if percent < 0:
            percent = 0
        elif percent > 1:
            percent = 1
        
        # print('a type', typeA['type'])
        
        # print('ladder percent:', percent)
        
        save = self.speed
        
        self.speed = speed
        
        b_led = self.match(typeB).copy()
        
        b = []
        
        for i, led_b in enumerate(b_led):
            if i < math.floor(self.size * percent):
                b.append(led_b)
        # print('b size:', len(b))
        
        # print('list b', len(b))

        self.speed = save
        
        
        a_led:list = self.match(typeA).copy()
        
        a:list = []
        
        for i, led_a in enumerate(a_led):
            if i < self.size - math.floor(self.size * percent):
                a.append(led_a)
        # print('a size:', len(a))
        
        # print('list a', len(a))
        

        
        res = b + a
        
        
        
        if len(res) > self.size:
            # print('too big!!', len(res))
            del res[self.size:]
        else:
            # print('led size', len(res))
            return res.copy()
        
        return self.array


# example led setup with port connections to PWM 0 and a length of 60
example_led_config = ADLeds(0, 60)

# initialize the leds
example_led_config.init()


# cycle this in the periodic
example_led_config.cycle()

# to set the leds to a specific type (RED, GREEN, BLUE)
example_led_config.setLED(Type.KStatic(255, 0, 0))

# change the speed of the rainbow
example_led_config.speed = 5

# to get the current type
example_led_config.getLED()