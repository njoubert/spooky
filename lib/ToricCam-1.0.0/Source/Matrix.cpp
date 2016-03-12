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

#include "toric/Matrix.h"

namespace toric
{
	Matrix3::Matrix3()
	{
		for(size_t i=0;i<3;i++)
			for(size_t j=0;j<3;j++)
				m_mat[i][j] = 0;
	}

	double & Matrix3::at( const size_t & i, const size_t & j )
	{
		return m_mat[i][j];
	}

	double & Matrix3::operator()( const size_t & i, const size_t & j )
	{
		return m_mat[i][j];
	}

	double const& Matrix3::operator()( const size_t & i, const size_t & j ) const
	{
		return m_mat[i][j];
	}

	toric::Vector3 Matrix3::getColumn( const size_t & j ) const
	{
		Vector3 col;
		for(int i=0;i<3;i++)
			col[i] = m_mat[i][j];
		return col;
	}

	toric::Vector3 Matrix3::getRow( const size_t & i ) const
	{
		Vector3 row;
		for(int j=0;j<3;j++)
			row[j] = m_mat[i][j];
		return row;
	}

	void Matrix3::swapColumn( const size_t & j, const Vector3 & col )
	{
		for(int i=0;i<3;i++)
			m_mat[i][j] = col[i];
	}

	void Matrix3::swapRow( const size_t & i, const Vector3 & row )
	{
		for(int j=0;j<3;j++)
			m_mat[i][j] = row[j];
	}

	double Matrix3::getDeterminant() const
	{
		double fCofactor00 = m_mat[1][1]*m_mat[2][2] -
			m_mat[1][2]*m_mat[2][1];
		double fCofactor10 = m_mat[1][2]*m_mat[2][0] -
			m_mat[1][0]*m_mat[2][2];
		double fCofactor20 = m_mat[1][0]*m_mat[2][1] -
			m_mat[1][1]*m_mat[2][0];

		double fDet =
			m_mat[0][0]*fCofactor00 +
			m_mat[0][1]*fCofactor10 +
			m_mat[0][2]*fCofactor20;

		return fDet;
	}

	Vector3 Matrix3::operator*( Vector3 const& v ) const
	{
		Vector3 res(0,0,0);

		for(int i=0;i<3;i++) // for each row of our matrix m
			for(int j=0;j<3;j++)
				res[i] += (m_mat[i][j] * v[j]) ;
		return res;
	}

}