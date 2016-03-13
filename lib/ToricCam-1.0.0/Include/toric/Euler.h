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

#ifndef TORIC_EULER_H
#define TORIC_EULER_H

namespace toric
{
	static double PI = 3.141592;
	static double TWO_PI = 2*PI;
	static double HALF_PI = 0.5*PI;

#define DegToRad	(PI/180.)
#define RadToDeg	(180./PI)

	/***************************************************************************************************/
	/// \class	RadianPi
	///
	/// \brief	representation of an angle in radian, within [-pi ; +pi] (default)
	/// \author	Christophe Lino
	/// \date	2012/07/29
	/***************************************************************************************************/

	class RadianPi
	{
	public:
		static RadianPi ZERO;
	private:
		double m_value;
	public:
		RadianPi(const double & r=0.0);

		const double& valueRadians()const;
		double valueDegrees() const;

		RadianPi operator-() const { return RadianPi(-m_value); }

		RadianPi operator*(double const & val) const;

		RadianPi operator/(double const & val) const;

	private:
		static double _modulo(const double & d);
	};

	/***************************************************************************************************/
	/// \class	Radian2Pi
	///
	/// \brief	representation of an angle in radian, within [0; 2*pi]
	/// \author	Christophe Lino
	/// \date	2012/07/29
	/***************************************************************************************************/

	class Radian2Pi
	{
	public:
		static Radian2Pi ZERO;
	private:
		double m_value;
	public:
		Radian2Pi(const double & r=0.0);

		const double& valueRadians() const;
		double valueDegrees() const;

	private:
		static double _modulo(const double & d);
	};
}

double cos(const toric::RadianPi & r);
double sin(const toric::RadianPi & r);
double tan(const toric::RadianPi & r);

double acos(const toric::RadianPi & r);
double asin(const toric::RadianPi & r);
double atan(const toric::RadianPi & r);

#endif