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

#ifndef TORIC_PLANE_H
#define TORIC_PLANE_H

#include "toric/Vector.h"

namespace toric
{
	class Plane
	{
	protected:
		double m_a, m_b, m_c, m_d;

	public:
		
		Plane(const double & a, const double & b, const double & c, const double & d);

		static Plane createPlaneFromUnitNormal(const Vector3 & normal, const Vector3 & point);

		static Plane createPlaneFromNormal(const Vector3 & normal, const Vector3 & point);

		static Plane createPlaneFromVectors(const Vector3 & vec1, const Vector3 & vec2, const Vector3 & point);

		static Plane createPlaneFromTriangle(const Vector3 & point1, const Vector3 & point2, const Vector3 & point3);

		const Vector3 getNormal() const { return Vector3(m_a,m_b,m_c); }

		double getDistance(const Vector3 & p) const { return getValue(p) / sqrt( m_a*m_a + m_b*m_b + m_c*m_c ); }

		double getValue(const Vector3 & p) const { return m_a * p.x() + m_b * p.y() + m_c * p.z() + m_d; }

		/// returns the normal projection of a point on the plane
		Vector3 getProjection( const Vector3 & p /*= Vector3(0,0,0)*/ ) const;

		/// returns true if the point belongs to the plane, false elsewise
		bool belongs(const Vector3 & point) const;
	};
}

#endif