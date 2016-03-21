/*
ToricSamples - sample code that provides examples of how to use ToricCam to compute viewpoints and to connect with a rendering engine.

Written in 2015 by Christophe Lino <christophe.lino@inria.fr>

To the extent possible under law, the author(s) have dedicated all copyright and related 
and neighboring rights to this software to the public domain worldwide. This software is 
distributed without any warranty.
You should have received a copy of the CC0 Public Domain Dedication along with this software. 
If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

You may use this sample code for anything you like, it is not covered by the
same license as the ToricCam library.
 */

#ifndef TORIC_SAMPLES_TWOTARGETS_H
#define TORIC_SAMPLES_TWOTARGETS_H

#include <toric/Camera.h>
#include <toric/Toric.h>

namespace toric
{
	namespace samples
	{
		struct TargetOOBS;
		
		class TwoSphereTargetProblem
		{
		private:
			const TargetOOBS	&m_target1, &m_target2;
			ToricManifold		m_manifold;
			mutable Camera				m_camera;

		public:
			enum Target{ Target1, Target2 };

			TwoSphereTargetProblem(const RadianPi& fovX, const double& screenAspect, const TargetOOBS &target1, const TargetOOBS &target2, const Vector2 &sposTarget1, const Vector2 &sposTarget2);

			const Camera& ComputeViewpointFromDistance(const double &distance, const Target whichOne) const;

			const Camera& ComputeViewpointFromScreenHeight(const double &screenHeight, Target whichOne) const;

			const Camera& ComputeViewpointFromVantage(const RadianPi &hAngle, const RadianPi &vAngle, Target whichOne) const;
		};
	}
}

#endif