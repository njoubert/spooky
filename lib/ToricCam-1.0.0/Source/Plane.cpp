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

#include <toric/Plane.h>

namespace toric
{
	Plane::Plane( const double & a, const double & b, const double & c, const double & d )
		: m_a(a), m_b(b), m_c(c), m_d(d)
	{

	}

	Plane Plane::createPlaneFromUnitNormal( const Vector3 & normal, const Vector3 & point )
	{
		Vector3 n = normal.normalized();
		double
			a = n.x(),
			b = n.y(),
			c = n.z(),
			d = -(n * point);

		return Plane(a,b,c,d);
	}

	Plane Plane::createPlaneFromNormal( const Vector3 & normal, const Vector3 & point )
	{
		Vector3 n(normal); n.normalize();
		return createPlaneFromUnitNormal(n, point);
	}


	Plane Plane::createPlaneFromVectors(const Vector3 & vec1, const Vector3 & vec2, const Vector3 & point)
	{
		Vector3 n(vec1 ^ vec2); n.normalize();
		return createPlaneFromUnitNormal(n, point);
	}

	Plane Plane::createPlaneFromTriangle( const Vector3 & point1, const Vector3 & point2, const Vector3 & point3 )
	{
		return createPlaneFromVectors(point2-point1, point3-point1, point1);
	}

	Vector3 Plane::getProjection( const Vector3 & p ) const
	{
		double u = p.x(), v = p.y(), w = p.z();
		double val = (m_a*u+m_b*v+m_c*w+m_d) / (m_a*m_a+m_b*m_b+m_c*m_c);
		double
			x0 = u - m_a * val,
			y0 = v - m_b * val,
			z0 = w - m_c * val;
		return Vector3(x0,y0,z0);
	}

	bool Plane::belongs(const Vector3 & point) const
	{
		return (m_a*point.x()+m_b*point.y()+m_c*point.z()+m_d) == 0;
	}
}