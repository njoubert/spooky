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

#include "toric/Quaternion.h"

namespace toric
{
	const Quaternion Quaternion::ZERO(0.0,0.0,0.0,0.0);
	const Quaternion Quaternion::IDENTITY(1.0,0.0,0.0,0.0);

	Quaternion::Quaternion(const double & w, const double & x, const double & y, const double & z)
		: m_s(w), m_v(x,y,z)
	{}

	/** \brief Constructor with vector/angle arguments */
	Quaternion::Quaternion( const double & s, const Vector3 & v )
		: m_s(s), m_v(v)
	{

	}

	void Quaternion::set( const double & s, const Vector3 & v )
	{
		m_s = s;
		m_v = v;
	}

	/** \brief Constructor with vector/angle arguments */
	Quaternion::Quaternion( const Vector3 & v, const RadianPi & angle )
		: m_s(cos(angle/2.0)), m_v(v.normalized()*sin(angle/2.0))
	{
		
	}

	void Quaternion::set( const Vector3 & v, const RadianPi & angle )
	{
		m_v = v.normalized()*sin(angle/2.0);
		m_s = cos(angle/2.0);
	}

	Quaternion::Quaternion( const Vector3 & xAxis, const Vector3 & yAxis, const Vector3 & zAxis )
	{
		FromAxes(xAxis,yAxis,zAxis);
	}

	Quaternion::Quaternion( const Matrix3 & rotationMatrix )
	{
		FromRotationMatrix(rotationMatrix);
	}

	Quaternion & Quaternion::operator= (Quaternion const & q)
	{
		m_s = q.m_s ;
		m_v = q.m_v ;
		return (*this) ;
	}

	void Quaternion::FromRotationMatrix (const Matrix3& mRot)
	{
		// Algorithm in Ken Shoemake's article in 1987 SIGGRAPH course notes
		// article "Quaternion Calculus and Fast Animation".

		double fTrace = mRot(0,0)+mRot(1,1)+mRot(2,2);
		double fRoot;

		if ( fTrace > 0.0 )
		{
			// |w| > 1/2, may as well choose w > 1/2
			fRoot = sqrt(fTrace + 1.0f);  // 2w
			m_s = 0.5f*fRoot;
			fRoot = 0.5f/fRoot;  // 1/(4w)
			m_v[0] = (mRot(2,1)-mRot(1,2))*fRoot;
			m_v[1] = (mRot(0,2)-mRot(2,0))*fRoot;
			m_v[2] = (mRot(1,0)-mRot(0,1))*fRoot;
		}
		else
		{
			// |w| <= 1/2
			static size_t s_iNext[3] = { 1, 2, 0 };
			size_t i = 0;
			if ( mRot(1,1) > mRot(0,0) )
				i = 1;
			if ( mRot(2,2) > mRot(i,i) )
				i = 2;
			size_t j = s_iNext[i];
			size_t k = s_iNext[j];

			fRoot = sqrt(mRot(i,i)-mRot(j,j)-mRot(k,k) + 1.0f);
			double* apkQuat[3] = { &m_v[0], &m_v[1], &m_v[2] };
			*apkQuat[i] = 0.5f*fRoot;
			fRoot = 0.5f/fRoot;
			m_s = (mRot(k,j)-mRot(j,k))*fRoot;
			*apkQuat[j] = (mRot(j,i)+mRot(i,j))*fRoot;
			*apkQuat[k] = (mRot(k,i)+mRot(i,k))*fRoot;
		}
	}

	void Quaternion::ToRotationMatrix (Matrix3& mRot) const
	{
		double fTx  = x()+x();
		double fTy  = y()+y();
		double fTz  = z()+z();
		double fTwx = fTx*w();
		double fTwy = fTy*w();
		double fTwz = fTz*w();
		double fTxx = fTx*x();
		double fTxy = fTy*x();
		double fTxz = fTz*x();
		double fTyy = fTy*y();
		double fTyz = fTz*y();
		double fTzz = fTz*z();

		mRot(0,0) = 1.0f-(fTyy+fTzz);
		mRot(0,1) = fTxy-fTwz;
		mRot(0,2) = fTxz+fTwy;
		mRot(1,0) = fTxy+fTwz;
		mRot(1,1) = 1.0f-(fTxx+fTzz);
		mRot(1,2) = fTyz-fTwx;
		mRot(2,0) = fTxz-fTwy;
		mRot(2,1) = fTyz+fTwx;
		mRot(2,2) = 1.0f-(fTxx+fTyy);
	}

	/// axis represent right, forward and up directions
	void Quaternion::FromAxes(const Vector3 & xAxis, const Vector3 & yAxis, const Vector3 & zAxis)
	{
		Matrix3 mRot;

		mRot.swapColumn(0, xAxis);
		mRot.swapColumn(1, yAxis);
		mRot.swapColumn(2, zAxis);
		
		FromRotationMatrix(mRot);
	}

	/// axis represent right, forward and up directions
	void Quaternion::ToAxes(Vector3 & xAxis, Vector3 & yAxis, Vector3 & zAxis) const
	{
		Matrix3 mRot;

		ToRotationMatrix(mRot);
		xAxis = mRot.getColumn(0);
		yAxis = mRot.getColumn(1);
		zAxis = mRot.getColumn(2);
	}

	Vector3 Quaternion::xAxis() const
	{
		double fTy  = 2.0f*y();
		double fTz  = 2.0f*z();
		double fTwy = fTy*w();
		double fTwz = fTz*w();
		double fTxy = fTy*x();
		double fTxz = fTz*x();
		double fTyy = fTy*y();
		double fTzz = fTz*z();

		return Vector3(1.0-(fTyy+fTzz), fTxy+fTwz, fTxz-fTwy);
	}

	Vector3 Quaternion::yAxis() const
	{
		double fTx  = 2.0f*x();
		double fTy  = 2.0f*y();
		double fTz  = 2.0f*z();
		double fTwx = fTx*w();
		double fTwz = fTz*w();
		double fTxx = fTx*x();
		double fTxy = fTy*x();
		double fTyz = fTz*y();
		double fTzz = fTz*z();

		return Vector3(fTxy-fTwz, 1.0-(fTxx+fTzz), fTyz+fTwx);
	}

	Vector3 Quaternion::zAxis() const
	{
		double fTx  = 2.0f*x();
		double fTy  = 2.0f*y();
		double fTz  = 2.0f*z();
		double fTwx = fTx*w();
		double fTwy = fTy*w();
		double fTxx = fTx*x();
		double fTxz = fTz*x();
		double fTyy = fTy*y();
		double fTyz = fTz*y();

		return Vector3(fTxz+fTwy, fTyz-fTwx, 1.0-(fTxx+fTyy));
	}

	double &	  Quaternion::s() { return m_s ; }
	Vector3 & Quaternion::v() { return m_v ; }
	
	const double &    Quaternion::s() const { return m_s ; }
	const Vector3 & Quaternion::v() const { return m_v ; }

	const double & Quaternion::w() const { return m_s;	}
	const double & Quaternion::x() const { return m_v[0]; }
	const double & Quaternion::y() const { return m_v[1]; }
	const double & Quaternion::z() const { return m_v[2]; }

	Quaternion Quaternion::operator* (Quaternion const & q) const
	{
		return Quaternion(m_s*q.m_s-m_v*q.m_v, q.m_v*m_s+m_v*q.m_s+(m_v^q.m_v)) ; 
	}

	Vector3 Quaternion::operator*( Vector3 const & v ) const
	{
		Vector3 uv, uuv;
		Vector3 qvec(x(), y(), z());
		uv = qvec.crossProduct(v);
		uuv = qvec.crossProduct(uv);
		uv = uv * (2.0 * w());
		uuv = uuv * 2.0;

		return v + uv + uuv;
	}

	Quaternion Quaternion::inverse() const
	{
		double fNorm = norm2();
		if ( fNorm > 0.0 )
		{
			double fInvNorm = 1.0f/fNorm;
			return Quaternion(w()*fInvNorm,-x()*fInvNorm,-y()*fInvNorm,-z()*fInvNorm);
		}
		else
		{
			// return an invalid result to flag the error
			return ZERO;
		}
	}

	double Quaternion::norm2() const
	{  
		return m_s*m_s+m_v.norm2() ; 
	}

	double Quaternion::norm() const
	{	
		return sqrt(norm2()) ; 
	}

	double Quaternion::dotProduct( const Quaternion & q ) const
	{
		return m_s * q.m_s + m_v * q.m_v;
	}
}