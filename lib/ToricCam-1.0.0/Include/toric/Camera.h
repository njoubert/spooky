/*
 This source file is part of ToricCam (a library for intuitive and efficient virtual camera control)
 For more info on the project, please contact Christophe Lino at christophe.lino@inria.fr
 
 Copyright (c) 2015 Christophe Lino
 Also see acknowledgments in readme.txt
 
 ToricCam is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 ToricCam is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this library.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef TORIC_CAMERA_H
#define TORIC_CAMERA_H

#include "toric/Euler.h"
#include "toric/Vector.h"
#include "toric/Quaternion.h"

namespace toric
{
	struct Camera
	{
		/// horizontal field of view (full frustum)
		RadianPi fovX; 
		/// screen aspect ratio = width / height
		double aspect; 
		/// world position
		Vector3 position; 
		/// world orientation
		Quaternion orientation; 

		/// Builds a camera with a 35mm lens, and a 16:9 aspect
		Camera() : fovX(43*DegToRad), aspect(16./9) {}

		/// Sets the horizontal field of view from the vertical field of view (full frustum)
		void setFovY(const RadianPi& fovY)
		{
			fovX = 2 * atan( tan(fovY * 0.5) * aspect );
		}

		/// Gets the vertical field of view (full frustum)
		RadianPi getFOVy() const
		{
			return 2 * atan2( tan(fovX.valueRadians() * 0.5), aspect );
		}
	};
}

#endif