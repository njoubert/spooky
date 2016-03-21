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

#include "SingleTarget.h"
#include "TargetOOBB.h"
#include "TargetOOBS.h"

#include <time.h>

namespace toric
{
	namespace samples
	{
		/************************************************************************/
		/* SingleSphereTargetProblem                                            */
		/************************************************************************/

		SingleSphereTargetProblem::SingleSphereTargetProblem( const RadianPi& fovX, const double& screenAspect, const TargetOOBS &target, const Vector2 &screen_pos )
			: m_target(target), m_screenPosition(screen_pos)
		{
			m_camera.fovX = fovX;
			m_camera.aspect = screenAspect;
		}

		const Camera& SingleSphereTargetProblem::ComputeViewpointFromScreenHeightAndVantage( const double &screen_height, const RadianPi &hAngle, const RadianPi &vAngle ) const
		{
			// vantage vector from the target center
			Vector3 vantage = m_target.getVantageVector(hAngle,vAngle); //vantage.normalize();

			// compute the actor's segment which will project vertically on the screen
			static Vector3 WorldUp(0,0,1);
			Vector3 axis = vantage ^ WorldUp ^ vantage; axis.normalize();
			Vector3
				wposTop		= m_target.position + axis * m_target.radius,
				wposBottom	= m_target.position - axis * m_target.radius;
			Vector2
				sposTop	  (m_screenPosition.x(), m_screenPosition.y()+screen_height),
				sposBottom(m_screenPosition.x(), m_screenPosition.y()-screen_height);

			// build a manifold from this segment and its vantage vector
			ToricManifold manifold = ToricManifold(m_camera.fovX, m_camera.aspect, sposTop, sposBottom, wposTop, wposBottom, vantage);

			// camera position
			m_camera.position = manifold.getPositionFromVantageToMiddleAB(vantage);
			//here, it is the same as:
			//m_camera.position = m_target.position + vantage * m_target.GetDistanceFromScreenHeight(m_camera.fovX, m_camera.aspect, screen_height);

			// camera orientation
			m_camera.orientation = manifold.computeOrientation(m_camera.position);

			return m_camera;
		}

		/************************************************************************/
		/* SingleBoxTargetProblem                                               */
		/************************************************************************/

		SingleBoxTargetProblem::SingleBoxTargetProblem( const RadianPi& fovX, const double& screenAspect, const TargetOOBB &target, const Vector2 &spos, const double &sheight )
			: m_target(target)
		{
			// build a manifold from its top point, its bottom point, its front vector, and its on-screen height
			Vector3
				wposTop		= m_target.position + m_target.orientation.zAxis() * m_target.dimension.z(),
				wposBottom	= m_target.position - m_target.orientation.zAxis() * m_target.dimension.z(),
				frontVector = m_target.orientation.yAxis();
			Vector2
				sposTop	  (spos.x(), spos.y()+sheight),
				sposBottom(spos.x(), spos.y()-sheight);
			m_manifold = ToricManifold(fovX, screenAspect, sposTop, sposBottom, wposTop, wposBottom, frontVector);
			
			m_camera.fovX = fovX;
			m_camera.aspect = screenAspect;
		}

		const Camera& SingleBoxTargetProblem::ComputeViewpointFromVantage( const RadianPi &hAngle, const RadianPi &vAngle ) const
		{
			// vantage vector from the target center
			Vector3 vantage = m_target.getVantageVector(hAngle,vAngle);

			// camera position
			m_camera.position = m_manifold.getPositionFromVantageToMiddleAB(vantage);

			// camera orientation
			m_camera.orientation = m_manifold.computeOrientation(m_camera.position);

			return m_camera;
		}
	}
}