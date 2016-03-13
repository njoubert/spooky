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

#ifndef TORIC_SAMPLES_SINGLETARGET_H
#define TORIC_SAMPLES_SINGLETARGET_H

#include <toric/Toric.h>
#include <toric/Camera.h>

namespace toric
{
	namespace samples
	{
		struct TargetOOBS;
		struct TargetOOBB;

		class SingleSphereTargetProblem
		{
		private:
			const TargetOOBS	&m_target;
			Vector2				m_screenPosition;
			mutable Camera		m_camera;

		public:
			SingleSphereTargetProblem(const RadianPi& fovX, const double& screenAspect, const TargetOOBS &target, const Vector2 &screen_pos);

			const Camera& ComputeViewpointFromScreenHeightAndVantage(const double &screen_height, const RadianPi &hAngle, const RadianPi &vAngle) const;
		};
			
		class SingleBoxTargetProblem
		{
		private:
			const TargetOOBB	&m_target;
			ToricManifold		m_manifold;
			mutable Camera				m_camera;

		public:
			SingleBoxTargetProblem(const RadianPi& fovX, const double& screenAspect, const TargetOOBB &target, const Vector2 &screen_pos, const double &screen_height);
			    
			const Camera& ComputeViewpointFromVantage(const RadianPi &hAngle, const RadianPi &vAngle) const;
		};
	}
}

#endif