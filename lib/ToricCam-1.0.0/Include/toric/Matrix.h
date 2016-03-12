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

#ifndef TORIC_MATRIX_H
#define TORIC_MATRIX_H

#include "toric/Vector.h"

namespace toric
{
	/***************************************************************************************************/
	/// \class	Matrix3
	///
	/// \brief	representation of 3x3 Matrix
	/// \author	Christophe Lino
	/// \date	2012/07/29
	/***************************************************************************************************/

	class Matrix3
	{
	private:		
		double m_mat[3][3];

	public:
		
		Matrix3();

		double & at(const size_t &  i, const size_t &  j);

		double & operator()(const size_t &  i, const size_t &  j);

		double const& operator()(const size_t &  i, const size_t &  j) const;

		Vector3 getColumn(const size_t &  j) const;
		
		Vector3 getRow(const size_t & i) const;

		void swapColumn(const size_t & j, const Vector3 & col);

		void swapRow(const size_t & i, const Vector3 & row);

		double getDeterminant() const;

		Vector3 operator*(Vector3 const& v) const;
	};
}

#endif