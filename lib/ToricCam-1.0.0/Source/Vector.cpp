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

#include "toric/Vector.h"
#include "toric/Quaternion.h"
#include "toric/Matrix.h"

namespace toric
{
	Vector3 Vector3::ZERO(0,0,0);
	Vector3 Vector3::UNIT_X(1,0,0);
	Vector3 Vector3::UNIT_Y(0,1,0);
	Vector3 Vector3::UNIT_Z(0,0,1);

	Vector2 Vector3::projectX() const { return Vector2(m_vec[1],m_vec[2]); }
	Vector2 Vector3::projectY() const { return Vector2(m_vec[0],m_vec[2]); }
	Vector2 Vector3::projectZ() const { return Vector2(m_vec[0],m_vec[1]); }

	Vector3 Vector3::crossProduct( const Vector3 & v ) const
	{
		return Vector3(
			m_vec[1]*v.m_vec[2]-m_vec[2]*v.m_vec[1],
			m_vec[2]*v.m_vec[0]-m_vec[0]*v.m_vec[2],
			m_vec[0]*v.m_vec[1]-m_vec[1]*v.m_vec[0]
		);
	}

	Vector3 Vector3::perpendicular() const
	{
		Vector3 res;
		if( z() == 0 ) // do the same as in 2d
		{
			res = Vector3(-y(),x(),z());
		}
		else
		{
			// satisfy the formula xx' + yy' + zz' = 0
			// by fixing 2 coords, then computing the 3rd
			// by using the dot product of the 2d sub-vectors
			Vector2 v(y(),z());
			double p = projectZ().dotProduct(v);
			res = Vector3(v[0],v[1],-p/z());
		}
		res.normalize();
		return res;
	}

	RadianPi Vector3::directedAngle( const Vector3 & vec, const Vector3 & normal ) const
	{
		Matrix3 m;
		m.swapRow(0, *this);
		m.swapRow(1, vec);
		m.swapRow(2, normal);
		double det = m.getDeterminant();

		RadianPi a = angle(vec);

		if( det > 0 )
			return a;
		else
			return -a;
	}
}