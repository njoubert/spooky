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

#include "TwoTargets.h"
#include "TargetOOBS.h"

#include <toric/ProjectionMatrix.h>

#include <iostream>

namespace toric
{
	namespace samples
	{
		TwoSphereTargetProblem::TwoSphereTargetProblem( const RadianPi& fovX, const double& screenAspect, const TargetOOBS &target1, const TargetOOBS &target2, const Vector2 &sposTarget1, const Vector2 &sposTarget2 )
			: m_target1(target1), m_target2(target2)
		{
			// build the appropriate manifold
			m_manifold = ToricManifold(fovX, screenAspect, sposTarget1, sposTarget2, m_target1.position, m_target2.position);
			
			// save static camera settings
			m_camera.fovX = fovX;
			m_camera.aspect = screenAspect;
		}

		const Camera& TwoSphereTargetProblem::ComputeViewpointFromDistance( const double &distance, const Target whichOne ) const
		{
			// get the values on the horizontal angle for which the exact distance is satisfied
			std::vector<Radian2Pi> thetas;
			if( whichOne == Target1 )
				thetas = m_manifold.getThetasFromDistanceToA(distance);
			else
				thetas = m_manifold.getThetasFromDistanceToB(distance);

			// if no solution, the exact distance constraint cannot be satisfied on the manifold
			if( thetas.empty() )
			{
				std::cout << "No solution exist !" << std::endl;
				m_camera.position = Vector3::ZERO;
				m_camera.orientation = Quaternion::IDENTITY;
			}
			// else: one can use any of the one or two solution(s) value(s) provided
			// with any value on the second angle "phi"
			else
			{
				std::cout << "There " << ( (thetas.size() == 1) ? "is one solution !" : "are two solutions !") << std::endl;
				Radian2Pi theta = thetas[ 0 ]; // but could be theta[1] if two solutions exist
				RadianPi phi = 0; // by default we use 0, but any value on this parameter provides a camera satisfying the distance constraint
				
				// camera setting expressed in world coordinates
				m_camera.position = m_manifold.computePosition( theta, phi );
				m_camera.orientation = m_manifold.computeOrientation(m_camera.position);
			}

			return m_camera;
		}

		const Camera& TwoSphereTargetProblem::ComputeViewpointFromScreenHeight( const double &screenHeight, Target whichOne ) const
		{
			// distance to the target
			double distance;
			switch(whichOne)
			{
			case Target1:
				distance = m_target1.GetDistanceFromScreenHeight(m_camera.fovX, m_camera.aspect, screenHeight);
				break;
			case Target2:
				distance = m_target2.GetDistanceFromScreenHeight(m_camera.fovX, m_camera.aspect, screenHeight);
				break;
			}

			// use the above method related to distance constraint
			return ComputeViewpointFromDistance(distance, whichOne);
		}

		const Camera& TwoSphereTargetProblem::ComputeViewpointFromVantage( const RadianPi &hAngle, const RadianPi &vAngle, Target whichOne ) const
		{
			// vantage vector of the target
			Vector3 vantage;
			switch(whichOne)
			{
			case Target1:
				vantage = m_target1.getVantageVector(hAngle,vAngle);
				break;
			case Target2:
				vantage = m_target2.getVantageVector(hAngle,vAngle);
				break;
			}
			
			// camera position
			switch(whichOne)
			{
			case Target1:
				m_camera.position = m_manifold.getPositionFromVantageToA(vantage);
				break;
			case Target2:
				m_camera.position = m_manifold.getPositionFromVantageToB(vantage);
				break;
			}
			// camera orientation
			m_camera.orientation = m_manifold.computeOrientation(m_camera.position);

			return m_camera;
		}
	}
}