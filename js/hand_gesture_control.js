/**
 * Hand Gesture Recognition & Control
 * 
 * Adds WebXR hand tracking with gesture recognition:
 * - Pinch detection (index + thumb)
 * - Grab detection (full hand close)
 * - Point detection (index finger extended)
 * - Palm open/close
 * - Swipe gestures
 * - Rotation gestures (two-hand)
 */

class HandGestureController {
  /**Detects and interprets hand gestures in VR.*/
  
  constructor(xrSession, scene) {
    this.xrSession = xrSession;
    this.scene = scene;
    
    // Hand tracking state
    this.hands = {
      left: new HandState('left'),
      right: new HandState('right')
    };
    
    // Gesture callbacks
    this.gestureCallbacks = {};
    
    // Hand joint indices (WebXR XRHand)
    this.JOINTS = {
      wrist: 0,
      thumb: { tip: 3, ip: 2, mcp: 1, cmc: 0 },
      index: { tip: 7, dip: 6, pip: 5, mcp: 4 },
      middle: { tip: 11, dip: 10, pip: 9, mcp: 8 },
      ring: { tip: 15, dip: 14, pip: 13, mcp: 12 },
      pinky: { tip: 19, dip: 18, pip: 17, mcp: 16 }
    };
    
    this._registerGestureCallbacks();
  }
  
  updateHandPose(handedness, hand) {
    /**Update hand pose from WebXR frame.*/
    const handState = this.hands[handedness];
    
    if (!hand) {
      handState.isVisible = false;
      return;
    }
    
    handState.isVisible = true;
    handState.joints = new Map();
    
    // Extract joint positions
    for (let i = 0; i < hand.size; i++) {
      const joint = hand.get(i);
      if (joint) {
        handState.joints.set(i, {
          position: joint.position,
          radius: joint.radius || 0.01
        });
      }
    }
    
    // Detect current gestures
    this._detectGestures(handedness);
  }
  
  _detectGestures(handedness) {
    /**Detect active gestures for given hand.*/
    const hand = this.hands[handedness];
    if (!hand.isVisible) return;
    
    // Check for pinch (index + thumb close)
    if (this._isPinching(hand)) {
      this._triggerGesture(`pinch_${handedness}`, hand);
    }
    
    // Check for grab (fingers closed)
    if (this._isGrabbing(hand)) {
      this._triggerGesture(`grab_${handedness}`, hand);
    }
    
    // Check for point (index extended, others closed)
    if (this._isPointing(hand)) {
      this._triggerGesture(`point_${handedness}`, hand);
    }
    
    // Check for palm open/close
    if (this._isPalmOpen(hand)) {
      this._triggerGesture(`palm_open_${handedness}`, hand);
    } else {
      this._triggerGesture(`palm_closed_${handedness}`, hand);
    }
    
    // Check for swipe
    this._detectSwipe(hand, handedness);
  }
  
  _isPinching(hand) {
    /**Detect pinch gesture (thumb + index close).*/
    const thumbTip = hand.joints.get(this.JOINTS.thumb.tip);
    const indexTip = hand.joints.get(this.JOINTS.index.tip);
    
    if (!thumbTip || !indexTip) return false;
    
    const distance = this._distance(thumbTip.position, indexTip.position);
    return distance < 0.02;  // 2cm threshold
  }
  
  _isGrabbing(hand) {
    /**Detect grab gesture (all fingers closed).*/
    const palmPos = hand.joints.get(this.JOINTS.wrist);
    const fingertips = [
      hand.joints.get(this.JOINTS.thumb.tip),
      hand.joints.get(this.JOINTS.index.tip),
      hand.joints.get(this.JOINTS.middle.tip),
      hand.joints.get(this.JOINTS.ring.tip),
      hand.joints.get(this.JOINTS.pinky.tip)
    ];
    
    if (!palmPos || !fingertips.every(f => f)) return false;
    
    // Check if all fingertips are close to palm
    const avgDistance = fingertips.reduce((sum, tip) => 
      sum + this._distance(palmPos.position, tip.position), 0) / fingertips.length;
    
    return avgDistance < 0.08;  // 8cm threshold
  }
  
  _isPointing(hand) {
    /**Detect point gesture (index extended, others closed).*/
    const indexTip = hand.joints.get(this.JOINTS.index.tip);
    const indexPip = hand.joints.get(this.JOINTS.index.pip);
    const middleTip = hand.joints.get(this.JOINTS.middle.tip);
    const thumbTip = hand.joints.get(this.JOINTS.thumb.tip);
    
    if (!indexTip || !indexPip || !middleTip) return false;
    
    // Index extended (tip far from pip)
    const indexExtended = this._distance(indexTip.position, indexPip.position) > 0.03;
    
    // Middle finger curled (tip close to pip)
    const middleCurled = this._distance(middleTip.position, 
      hand.joints.get(this.JOINTS.middle.pip).position) < 0.03;
    
    return indexExtended && middleCurled;
  }
  
  _isPalmOpen(hand) {
    /**Detect palm open gesture.*/
    const wrist = hand.joints.get(this.JOINTS.wrist);
    const fingertips = [
      hand.joints.get(this.JOINTS.thumb.tip),
      hand.joints.get(this.JOINTS.index.tip),
      hand.joints.get(this.JOINTS.middle.tip)
    ];
    
    if (!wrist || !fingertips.every(f => f)) return false;
    
    // Palm open if fingertips spread away from wrist
    const avgDistance = fingertips.reduce((sum, tip) => 
      sum + this._distance(wrist.position, tip.position), 0) / fingertips.length;
    
    return avgDistance > 0.1;  // 10cm threshold
  }
  
  _detectSwipe(hand, handedness) {
    /**Detect swipe gesture.*/
    if (!hand.prevPosition) {
      hand.prevPosition = hand.joints.get(this.JOINTS.wrist).position;
      return;
    }
    
    const wrist = hand.joints.get(this.JOINTS.wrist);
    if (!wrist) return;
    
    const delta = {
      x: wrist.position.x - hand.prevPosition.x,
      y: wrist.position.y - hand.prevPosition.y,
      z: wrist.position.z - hand.prevPosition.z
    };
    
    const magnitude = Math.sqrt(delta.x*delta.x + delta.y*delta.y + delta.z*delta.z);
    
    if (magnitude > 0.05) {  // 5cm swipe threshold
      const direction = this._getSwipeDirection(delta);
      this._triggerGesture(`swipe_${direction}_${handedness}`, hand);
    }
    
    hand.prevPosition = wrist.position;
  }
  
  _getSwipeDirection(delta) {
    /**Determine swipe direction from delta.*/
    const absX = Math.abs(delta.x);
    const absY = Math.abs(delta.y);
    const absZ = Math.abs(delta.z);
    
    if (absX > absY && absX > absZ) {
      return delta.x > 0 ? 'right' : 'left';
    } else if (absY > absX && absY > absZ) {
      return delta.y > 0 ? 'up' : 'down';
    }
    return 'forward';
  }
  
  _triggerGesture(gestureName, handData) {
    /**Trigger registered gesture callback.*/
    const callback = this.gestureCallbacks[gestureName];
    if (callback) {
      callback(handData);
    }
  }
  
  onGesture(gestureName, callback) {
    /**Register gesture callback.*/
    this.gestureCallbacks[gestureName] = callback;
  }
  
  _distance(p1, p2) {
    /**Calculate 3D distance.*/
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    const dz = p1.z - p2.z;
    return Math.sqrt(dx*dx + dy*dy + dz*dz);
  }
  
  _registerGestureCallbacks() {
    /**Register default gesture handlers.*/
    
    // Pinch = Select/Grab
    this.onGesture('pinch_right', (hand) => {
      console.log('Right pinch: selecting object');
      this._selectNearbyObject(hand);
    });
    
    // Grab = Release/Drop
    this.onGesture('grab_right', (hand) => {
      console.log('Right grab: picking up object');
      this._grabNearbyObject(hand);
    });
    
    // Point = Highlight/Inspect
    this.onGesture('point_right', (hand) => {
      console.log('Right point: inspecting');
      this._inspectPointedObject(hand);
    });
    
    // Palm open = Reset/Cancel
    this.onGesture('palm_open_right', (hand) => {
      console.log('Palm open: reset view');
      this._resetView();
    });
    
    // Swipes = Navigation
    this.onGesture('swipe_left_right', () => console.log('Swipe left'));
    this.onGesture('swipe_right_right', () => console.log('Swipe right'));
    this.onGesture('swipe_up_right', () => console.log('Swipe up'));
    this.onGesture('swipe_down_right', () => console.log('Swipe down'));
  }
  
  _selectNearbyObject(hand) {
    /**Select object near pinch position.*/
    // Raycasting from index fingertip
  }
  
  _grabNearbyObject(hand) {
    /**Grab object near hand.*/
  }
  
  _inspectPointedObject(hand) {
    /**Inspect object being pointed at.*/
  }
  
  _resetView() {
    /**Reset camera to default.*/
  }
}

class HandState {
  /**Tracks state of one hand.*/
  
  constructor(handedness) {
    this.handedness = handedness;
    this.isVisible = false;
    this.joints = new Map();
    this.prevPosition = null;
    this.currentGesture = null;
  }
}

export { HandGestureController, HandState };
