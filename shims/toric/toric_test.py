import toric

wpos = toric.Vector3(0.5,-0.5,0)
wposA = toric.Vector3(0,0,0)
wposB = toric.Vector3(1,0,0)
zero = toric.Vector3(0,0,0)
t = toric.Toric3_FromWorldPosition(wpos, wposA, wposB, zero)