import toric

cam = toric.Vector3(0.5,-0.5,0)
PA = toric.Vector3(0,0,0)
PB = toric.Vector3(1,0,0)

print "CAM:(%d,%d,%d)" % (cam.x(), cam.y(), cam.z())
print "PA:(%d,%d,%d)" % (PA.x(), PA.y(), PA.z())
print "PB:(%d,%d,%d)" % (PB.x(), PB.y(), PB.z())

t = toric.Toric3_FromWorldPosition(cam,PA,PB)

print "Toric3: (a=%.2f, t=%.2f, p=%.2f)" % (t.getAlpha().valueDegrees(), t.getTheta().valueDegrees(), t.getPhi().valueDegrees())
