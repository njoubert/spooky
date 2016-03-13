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

#ifndef TORIC_VECTOR_H
#define TORIC_VECTOR_H

#include "Euler.h"

#include <math.h>
#include <algorithm>

#define clamp(val, min_val, max_val)	std::max((min_val), std::min((max_val), (val)))

namespace toric
{

	template<size_t SIZE>
	class Vector
	{
	protected:
		double m_vec[SIZE];

	public:
		Vector(Vector<SIZE> const & v)
		{
			for(size_t i=0;i<SIZE;i++) m_vec[i] = v.m_vec[i];
		}

		Vector(const double & val=0)
		{
			for(size_t i=0;i<SIZE;i++)
				m_vec[i] = val;
		}

		double & operator [] (size_t i) { return m_vec[i]; }

		const double & operator [] (size_t i) const { return m_vec[i]; }

		double dotProduct (const Vector<SIZE> & v) const
		{
			double p = 0;
			for(size_t i=0;i<SIZE;i++)
				p += m_vec[i] * v.m_vec[i];
			return p;
		}

		/// dot product
		double operator*(const Vector<SIZE> & v) const
		{
			return dotProduct(v);
		}

		double norm2() const
		{
			return dotProduct(*this);
		}

		double norm() const
		{ 
			return sqrt(norm2());
		}

		Vector<SIZE> normalized() const
		{
			double n = norm();
			Vector<SIZE> res;
			if(n)
			{
				for(size_t i=0;i<SIZE;i++) res[i] = m_vec[i] / n;
			}
			return res;
		}

		void normalize()
		{
			double n = norm();
			if(n)
			{
				for(size_t i=0;i<SIZE;i++) m_vec[i] /= n;
			}
		}

		RadianPi angle(const Vector<SIZE> & vec) const
		{
			Vector
				u = normalized(),
				v = vec.normalized();

			double lenProduct = u.norm() * v.norm();

			// Divide by zero check
			if(lenProduct < 1e-6)
				lenProduct = 1e-6;

			double f = u.dotProduct(v) / lenProduct;

			f = clamp(f, -1.0, +1.0);

			if( f < 0 )
				return PI - 2 * asin( (-v-u).norm()/2.0);
			else
				return 2 * asin((v-u).norm()/2.0);
		}

		Vector<SIZE> operator+(const Vector<SIZE> & v) const
		{
			Vector<SIZE> res;
			for(size_t i=0;i<SIZE;i++)
				res[i] = m_vec[i] + v.m_vec[i];
			return res;
		}

		Vector<SIZE> operator-(const Vector<SIZE> & v) const
		{
			Vector<SIZE> res;
			for(size_t i=0;i<SIZE;i++)
				res[i] = m_vec[i] - v.m_vec[i];
			return res;
		}

		Vector<SIZE> operator-() const
		{
			Vector<SIZE> res;
			for(size_t i=0;i<SIZE;i++)
				res[i] = - m_vec[i];
			return res;
		}

		Vector<SIZE> operator*(double const & val) const
		{
			Vector<SIZE> res;
			for(size_t i=0;i<SIZE;i++)
				res[i] = m_vec[i] * val;
			return res;
		}

		Vector<SIZE> operator/ (double const & val) const
		{
			Vector<SIZE> result ;
			for(size_t cpt=0 ; cpt<SIZE ; cpt++)
				result[cpt] = m_vec[cpt]/val ;
			return result ;			
		}

		void negate()
		{
			for(size_t i=0;i<SIZE;i++)
				m_vec[i] = -m_vec[i];
		}
	};

	/***************************************************************************************************/
	///  \class	Vector2
	///
	/// \brief	2d vector representation (x,y)
	///
	/// \author	Christophe Lino
	/// \date	2012/07/29
	/***************************************************************************************************/

	class Vector2 : public Vector<2>
	{
	public:
		Vector2(const double & x=0, const double & y=0)
		{
			m_vec[0] = x;
			m_vec[1] = y;
		}

		Vector2(Vector<2> const & v) : Vector<2>(v)
		{

		}

		const double & x() const { return m_vec[0]; }
		const double & y() const { return m_vec[1]; }

		Vector2& rotate90()
		{
			double tmp = m_vec[0];
			m_vec[0] = -m_vec[1]; 
			m_vec[1] = tmp; 
			return (*this);
		}

		inline Vector2& rotate180() { negate(); return (*this); }

		inline Vector2& rotate270() { rotate90(); rotate180(); return (*this); }

		inline Vector2& rotate( const RadianPi & theta )
		{
			double
				x = cos(theta) * m_vec[0] - sin(theta) * m_vec[1],
				y = sin(theta) * m_vec[0] + cos(theta) * m_vec[1];
			m_vec[0] = x;
			m_vec[1] = y;
			return (*this);
		}

		Vector2 rotated90() const { return Vector2(-m_vec[1], m_vec[0]) ; }
		Vector2 rotated180() const { return Vector2(-m_vec[0], -m_vec[1]); }
		Vector2 rotated270() const { return (*this).rotated90().rotated180() ; }
	};

	/***************************************************************************************************/
	///  \class	Vector3
	///
	/// \brief	3d vector representation (x,yz)
	///
	/// \author	Christophe Lino
	/// \date	2012/07/29
	/***************************************************************************************************/

	class Vector3 : public Vector<3>
	{
	public:
		static Vector3 ZERO;
		static Vector3 UNIT_X;
		static Vector3 UNIT_Y;
		static Vector3 UNIT_Z;

		Vector3(const double & x=0, const double & y=0, const double & z=0)
		{
			m_vec[0] = x;
			m_vec[1] = y;
			m_vec[2] = z;
		}

		Vector3(Vector<3> const & v) : Vector(v)
		{

		}

		const double & x() const { return m_vec[0]; }
		const double & y() const { return m_vec[1]; }
		const double & z() const { return m_vec[2]; }

		Vector2 projectX() const;
		Vector2 projectY() const;
		Vector2 projectZ() const;

		Vector3 crossProduct (const Vector3 & v) const;

		/// cross product
		Vector3 operator^(const Vector3 & v) const
		{
			return crossProduct(v);
		}

		Vector3 perpendicular() const;

		//RadianPi directedAngle( const Vector3 & vec, const Vector3 & normal ) const;
	};
}

#endif