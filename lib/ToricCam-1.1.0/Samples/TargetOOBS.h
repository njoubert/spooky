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

#ifndef TORIC_SAMPLES_TARGET_SPHERE_H
#define TORIC_SAMPLES_TARGET_SPHERE_H

#include <toric/Euler.h>
#include <toric/Vector.h>
#include <toric/Quaternion.h>
#include <toric/ProjectionMatrix.h>

#include <iostream>

namespace toric
{
	namespace samples
	{
		/// Target's as a bounding sphere
		struct TargetOOBS
		{
			Vector3		position;
			Quaternion	orientation;
			double		radius;

			Vector3 getVantageVector(const RadianPi &hAngle, const RadianPi &vAngle) const
			{
				// target's coordinate system
				Vector3 right = orientation.xAxis();
				Vector3 front = orientation.yAxis();
				Vector3 up = orientation.zAxis();

				// horizontal angle taken from front
				Quaternion qH(up, hAngle); 
				// vertical angle
				Quaternion qV(qH * right, vAngle); 
				// view vector
				Vector3 vantage = qV * qH * front;

				return vantage;
			}

			double GetDistanceFromScreenHeight(RadianPi fovX, double aspect, double screenHeight) const
			{
				double worldHeight = radius * 2;
				double Sx, Sy;
				ProjectionMatrix::ComputeScale(fovX, aspect, Sx, Sy);
				return (worldHeight * Sy) / (2 * screenHeight);
			}

			double GetScreenHeightFromDistance(RadianPi fovX, double aspect, double distance) const
			{
				double worldHeight = radius * 2;
				double Sx, Sy;
				ProjectionMatrix::ComputeScale(fovX, aspect, Sx, Sy);
				return (worldHeight * Sy) / (2 * distance);
			}

			/************************************************************************/
			/* Methods to check output viewpoints                                   */
			/************************************************************************/

			struct VisualFeatures
			{
				Vector2		screenPosition;
				double		screenHeight;
				RadianPi	horizontalAngle; 
				RadianPi	verticalAngle; 
			};

			VisualFeatures GetVisualFeaturesFromViewpoint(const Camera &cam)
			{
				VisualFeatures f;
				ProjectionMatrix pm(cam);
				Vector3 vecToCamera = cam.position-position;
				// screen position
				{
					f.screenPosition = pm.screenProjection(position);
				}
				// screen height
				{
					Vector3 vantage = cam.position-position; vantage.normalize();
					Vector3 axis = vantage ^ Vector3(0,0,1) ^ vantage; axis.normalize();
					Vector3
						wposTop		= position + axis * radius,
						wposBottom	= position - axis * radius;
					Vector2 topScreen = pm.screenProjection(wposTop);
					Vector2 botScreen = pm.screenProjection(wposBottom);
					std::cout << "top: (" << topScreen.x() << ", " << topScreen.y() << ")" << std::endl;
					std::cout << "bot: (" << botScreen.x() << ", " << botScreen.y() << ")" << std::endl;
					std::cout << "height: " << (topScreen.y()-botScreen.y()) * 0.5 << std::endl;
					f.screenHeight = GetScreenHeightFromDistance(cam.fovX, cam.aspect, (cam.position-position).norm());
				}
				// horizontal/vertical angle
				{
					Vector3 zAxis = orientation.zAxis();
					Vector3 right = vecToCamera ^ orientation.zAxis();
					f.verticalAngle = HALF_PI - vecToCamera.directedAngle(zAxis, right).valueRadians();
					Quaternion qV(right, f.verticalAngle);
					Vector3 vec = qV.inverse() * vecToCamera;
					f.horizontalAngle = orientation.yAxis().directedAngle(vec, zAxis);
				}

				return f;
			}
		};
	}
}

#endif