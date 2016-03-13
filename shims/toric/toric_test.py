import toric

cam = toric.Vector3(0.5,-0.5,0)
PA = toric.Vector3(0,0,0)
PB = toric.Vector3(1,0,0)

print "CAM:(%.2f,%.2f,%.2f)" % (cam.x(), cam.y(), cam.z())
print "PA:(%.2f,%.2f,%.2f)" % (PA.x(), PA.y(), PA.z())
print "PB:(%.2f,%.2f,%.2f)" % (PB.x(), PB.y(), PB.z())

t = toric.Toric3_FromWorldPosition(cam,PA,PB)

print "Toric3: (a=%.2f, t=%.2f, p=%.2f)" % (t.getAlpha().valueDegrees(), t.getTheta().valueDegrees(), t.getPhi().valueDegrees())

cam_back = toric.Toric3_ToWorldPosition(t, PA, PB)

print "Recovering CAM:"

print "CAM_BACK:(%.2f,%.2f,%.2f)" % (cam_back.x(), cam_back.y(), cam_back.z())
