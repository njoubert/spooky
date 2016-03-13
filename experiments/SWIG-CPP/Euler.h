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