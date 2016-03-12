#include "toric/Toric.h"

#include "Camera.h"

using namespace toric;

int main()
{
	/** in the following code sample we will compute camera viewpoints satisfying a common on-screen positioning of two targets **/

	// static camera settings
	const RadianPi fieldOfViewX = 43 * DegToRad;
	const double aspectRatio = 16./9;

	// targets' world positions
	const Vector3 wposA(0,0,0);
	const Vector3 wposB(10,10,0);

	// targets' screen positions in [-1;1]^2 (we here apply the rule of thirds)
	const Vector2 sposA(-0.33, +0.33);
	const Vector2 sposB(+0.33, +0.33);

	// we build the manifold surface
	toric::ToricManifold manifold(fieldOfViewX, aspectRatio, sposA, sposB, wposA, wposB); 

	// we can now compute camera viewpoints which satisfy the on-screen positioning, ie on the manifold surface
	const int N = 10;
	Camera cameras[N*N];
	for(size_t t=0; t<N; t++)
	{
		Radian2Pi theta = manifold.getThetaFromRatio( double(t+1) / (N+1) );
		// here is an equivalent way to do
		// Radian2Pi theta = manifold.getMaxTheta() * ( double(t+1) / (N+1) );
		for (size_t p=0; p<10; p++)
		{
			RadianPi phi = double(p) * TWO_PI / N;
			cameras[t*N+p].position = manifold.computePosition(theta, phi);
			cameras[t*N+p].orientation = manifold.computeOrientation(cameras[t*N+p].position);
		}
	}

	return 0;
}