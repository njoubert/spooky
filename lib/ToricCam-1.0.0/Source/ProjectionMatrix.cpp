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

#include "toric/ProjectionMatrix.h"

namespace toric
{
	void ProjectionMatrix::ComputeScale(const RadianPi & fovX, const double & aspect, double & Sx, double & Sy)
	{
		double
			tanX = tan(fovX.valueRadians()/2),
			tanY = tanX / aspect;
		Sx = 1.0 / tanX;
		Sy = 1.0 / tanY;
	}

	void ProjectionMatrix::ComputeScale( const RadianPi & fovX, const RadianPi & fovY, double & Sx, double & Sy )
	{
		double tanX = tan(fovX.valueRadians()/2);
		double tanY = tan(fovY.valueRadians()/2);
		Sx = 1.0 / tanX;
		Sy = 1.0 / tanY;
	}

	Vector3 ProjectionMatrix::GetVectorInCameraSpace( const Vector3& screenProj, const RadianPi& fovX, const RadianPi& fovY )
	{
		double Sx,Sy;
		ComputeScale(fovX,fovY,Sx,Sy);
		return GetVectorInCameraSpace(screenProj, Sx, Sy);
	}

	double sign(double x)
	{
		if( x < 0 ) return -1;
		if( x > 0 ) return +1;
		return 0;
	}

	Vector3 ProjectionMatrix::GetVectorInCameraSpace( const Vector3& screenProj, const double& Sx, const double& Sy )
	{
		Vector3 vec;
		if( screenProj.z() == 0 )
			vec = Vector3(screenProj.x(), 0, screenProj.y());
		else
			vec = Vector3(screenProj.x()/Sx, sign(screenProj.z()), screenProj.y()/Sy);
		return vec;
	}

	ProjectionMatrix::ProjectionMatrix()
		: m_position(), m_rotation(), m_Sx(0), m_Sy(0)
	{

	}

	ProjectionMatrix::ProjectionMatrix( const Camera & camera )
	{
		m_position = camera.position;
		m_rotation = BuildMatrix(camera.orientation);
		ComputeScale(camera.fovX, camera.aspect, m_Sx, m_Sy);
	}

	ProjectionMatrix::ProjectionMatrix( const RadianPi & fovX, const double & aspect, const Vector3 & p, const Matrix3 & r )
		: m_position(p), m_rotation(r)
	{
		ComputeScale(fovX, aspect, m_Sx, m_Sy);
	}

	ProjectionMatrix::ProjectionMatrix( const RadianPi & fovX, const RadianPi & fovY, const Vector3 & p, const Matrix3 & r )
		: m_position(p), m_rotation(r)
	{
		ComputeScale(fovX, fovY, m_Sx, m_Sy);
	}

	ProjectionMatrix::ProjectionMatrix( const RadianPi & fovX, const double & aspect, const Vector3 & p, const Quaternion & q )
		: m_position(p), m_rotation(BuildMatrix(q))
	{
		ComputeScale(fovX, aspect, m_Sx, m_Sy);
	}

	ProjectionMatrix::ProjectionMatrix( const RadianPi & fovX, const RadianPi & fovY, const Vector3 & p, const Quaternion & q )
		: m_position(p), m_rotation(BuildMatrix(q))
	{
		ComputeScale(fovX, fovY, m_Sx, m_Sy);
	}

	void ProjectionMatrix::setFieldOfView( const RadianPi & fovX, const double & aspect )
	{
		ComputeScale(fovX, aspect, m_Sx, m_Sy);
	}

	void ProjectionMatrix::setFieldOfView( const RadianPi & fovX, const RadianPi & fovY )
	{
		ComputeScale(fovX, fovY, m_Sx, m_Sy);
	}

	void ProjectionMatrix::setPosition( const Vector3 & p )
	{
		m_position = p; 
	}

	void ProjectionMatrix::setOrientation( const Quaternion & q ) 
	{ 
		m_rotation = BuildMatrix(q);
	}

	Vector2 ProjectionMatrix::screenProjection( const Vector3 & worldCoords ) const
	{
		Vector3 cameraCoords = worldCoords;
		for(size_t i=0; i<3; i++) cameraCoords[i] -= m_position[i]; 
		cameraCoords = m_rotation * cameraCoords;
		Vector2 screenCoords( cameraCoords.x() * m_Sx / cameraCoords.z(), cameraCoords.y() * m_Sy / cameraCoords.z() );
		return screenCoords;
	}

	Matrix3 ProjectionMatrix::BuildMatrix( const Vector3 & right, const Vector3 & forward, const Vector3 & up )
	{
		Matrix3 m;

		m.swapRow(0, right);
		m.swapRow(1, up);
		m.swapRow(2, forward);

		return m;
	}

	Matrix3 ProjectionMatrix::BuildMatrix( const Quaternion & orientation )
	{
		Vector3	r, f, u;
		orientation.ToAxes(r,f,u);

		return BuildMatrix(r, f, u);
	}
}