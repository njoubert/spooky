/*
 This source file is part of ToricCam (a library for intuitive and efficient virtual camera control)
 For more info on the project, please contact Christophe Lino at christophe.lino@inria.fr
 
 Copyright (c) 2015 Christophe Lino
 Also see acknowledgments in readme.txt
 
 This library is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this library.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef TORIC_PROJECTION_MATRIX_H
#define TORIC_PROJECTION_MATRIX_H

#include "toric/Camera.h"
#include "toric/Euler.h"
#include "toric/Matrix.h"
#include "toric/Quaternion.h"
#include "toric/Vector.h"


namespace toric
{
	class ProjectionMatrix
	{
	private:
		Vector3 m_position;
		Matrix3 m_rotation;
		double m_Sx, m_Sy;
		
	public:
		ProjectionMatrix();

		ProjectionMatrix(const Camera & camera);

		ProjectionMatrix(const RadianPi & fovX, const double & aspect, const Vector3 & p, const Quaternion & q);

		ProjectionMatrix(const RadianPi & fovX, const RadianPi & fovY, const Vector3 & p, const Quaternion & q);
		
		ProjectionMatrix(const RadianPi & fovX, const double & aspect, const Vector3 & p, const Matrix3 & r);

		ProjectionMatrix(const RadianPi & fovX, const RadianPi & fovY, const Vector3 & p, const Matrix3 & r);
		
		void setFieldOfView(const RadianPi & fovX, const double & aspect);

		void setFieldOfView(const RadianPi & fovX, const RadianPi & fovY);

		void setPosition(const Vector3 & p);

		void setOrientation(const Quaternion & q);

		Vector2 screenProjection( const Vector3 & worldCoords ) const;

		inline const double & getSx() const { return m_Sx; }
		inline const double & getSy() const { return m_Sy; }

	public:
		static void ComputeScale(const RadianPi & fovX, const double & aspect, double & Sx, double & Sy);
		static void ComputeScale(const RadianPi & fovX, const RadianPi & fovY, double & Sx, double & Sy);

		static Vector3 GetVectorInCameraSpace(const Vector3& screenProj, const RadianPi& fovX, const RadianPi& fovY);
		static Vector3 GetVectorInCameraSpace(const Vector3& screenProj, const double& Sx, const double& Sy);

	private:
		static Matrix3 BuildMatrix(const Vector3 & right, const Vector3 & forward, const Vector3 & up);
		static Matrix3 BuildMatrix(const Quaternion & orientation);
	};
}

#endif