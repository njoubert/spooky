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

#ifndef TORIC_SAMPLES_TARGET_BOX_H
#define TORIC_SAMPLES_TARGET_BOX_H

#include <toric/Euler.h>
#include <toric/Vector.h>
#include <toric/Quaternion.h>
#include <toric/ProjectionMatrix.h>

#include <iostream>

namespace toric
{
	namespace samples
	{
		/// Target's as a bounding box
		struct TargetOOBB
		{
			Vector3		position;
			Quaternion	orientation;
			Vector3		dimension;

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

			/************************************************************************/
			/* Methods to check output viewpoints                                   */
			/************************************************************************/

			struct VisualFeatures
			{
				Vector2		screenPositionTop;
				Vector2		screenPositionBottom;
				RadianPi	horizontalAngle; 
				RadianPi	verticalAngle; 
			};

			VisualFeatures GetVisualFeaturesFromViewpoint(const Camera &cam)
			{
				VisualFeatures f;
				ProjectionMatrix pm(cam);
				Vector3 vecToCamera = cam.position-position;
				// screen positions
				{
					f.screenPositionTop		= pm.screenProjection(position+orientation.zAxis()*dimension.z());
					f.screenPositionBottom	= pm.screenProjection(position-orientation.zAxis()*dimension.z());
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