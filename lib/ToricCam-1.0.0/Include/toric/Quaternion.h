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

#ifndef TORIC_QUATERNION_H
#define TORIC_QUATERNION_H

#include "toric/Vector.h"
#include "toric/Matrix.h"
#include "toric/Euler.h"

namespace toric
{
	/***************************************************************************************************/
	/// \class	Quaternion
	///
	/// \brief	representation of a quaternion rotation
	/// \author	Christophe Lino
	/// \date	2012/07/29
	/***************************************************************************************************/

	class Quaternion
	{
	public:
		static const Quaternion ZERO;
		static const Quaternion IDENTITY;
	protected:
		/// scalar part
		double  m_s ;
		/// vector part
		Vector3 m_v ;

	public:

		/***************************************************************************************************/
		/// \brief	Constructor with raw quaternion coordinates
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Quaternion(const double &  w=1, const double &  x=0, const double &  y=0, const double &  z=0);

		/***************************************************************************************************/
		/// \brief	Constructor with a vector and an angle
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Quaternion(const Vector3 & v, const RadianPi & angle);

		/***************************************************************************************************/
		/// \brief	Constructor with quaternion scalar and vector parts 
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Quaternion(const double & s, const Vector3 & v);

		/***************************************************************************************************/
		/// \brief	Constructor with axes (right-handed coordinate system where x=right, y=forward, z=up)
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Quaternion(const Vector3 & xAxis, const Vector3 & yAxis, const Vector3 & zAxis);

		/***************************************************************************************************/
		/// \brief	Constructor with rotation matrix
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Quaternion(const Matrix3 & rotationMatrix);

		/***************************************************************************************************/
		/// \brief	Sets the quaternion from scalar and vector parts
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		void set(const double & s, const Vector3 & v);
		
		/***************************************************************************************************/
		/// \brief	Sets the quaternion from vector and angle
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		void set(const Vector3 & v, const RadianPi & angle);

		/***************************************************************************************************/
		/// \brief	Sets the quaternion from axes (right-handed coordinate system where x=right, y=forward, z=up)
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		void FromAxes(const Vector3 & xAxis, const Vector3 & yAxis, const Vector3 & zAxis);

		/***************************************************************************************************/
		/// \brief	Gets the axes from a quaternion (right-handed coordinate system where x=right, y=forward, z=up)
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		void ToAxes(Vector3 & xAxis, Vector3 & yAxis, Vector3 & zAxis) const;

		/***************************************************************************************************/
		/// \brief	Sets the quaternion from a rotation matrix
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/
		
		void FromRotationMatrix(const Matrix3 & mRot);

		/***************************************************************************************************/
		/// \brief	Gets the rotation matrix from a quaternion
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		void ToRotationMatrix(Matrix3& mRot) const;

		Vector3 xAxis() const;
		Vector3 yAxis() const;
		Vector3 zAxis() const;

		/***************************************************************************************************/
		/// \brief	Get scalar part
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		double & s();

		/***************************************************************************************************/
		/// \brief	Get scalar part
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		const double & s() const;

		/***************************************************************************************************/
		/// \brief	Get vector part
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		const Vector3 & v() const;

		/***************************************************************************************************/
		/// \brief	Get vector part
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Vector3 & v();

		const double & w() const;
		const double & x() const;
		const double & y() const;
		const double & z() const;
 
		/***************************************************************************************************/
		/// \brief	Combination of quaternions
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Quaternion operator* (Quaternion const & q) const;

		/***************************************************************************************************/
		/// \brief	Rotation of a vector by a quaternion
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Vector3 operator* (Vector3 const & v) const;

		/***************************************************************************************************/
		/// \brief	Inverse quaternion q^-1
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Quaternion inverse() const;

		/***************************************************************************************************/
		/// \brief	Squared norm of the quaternion
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		double norm2() const;

		/***************************************************************************************************/
		/// \brief	Norm of the quaternion
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		double norm() const;

		/***************************************************************************************************/
		/// \brief	Dot product of the quaternions
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		double dotProduct(const Quaternion & q) const;

		/***************************************************************************************************/
		/// \brief	Assignment
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		Quaternion & operator= (Quaternion const & q);

		/***************************************************************************************************/
		/// \brief	Normalize the current quaternion
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		// HACK NJ: IT APPEARS THIS FUNCTION IS NOT DEFINED ANYWHERE
		// Quaternion & normalise() ;
	}; 
}

#endif
