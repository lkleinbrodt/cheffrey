#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sugarcube.py
"""Convert cooking ingredients to various measurements

Usage and examples:
>>> (1 * Volume.cup).to(Volume.milliliter)
240 ml
>>> (250 * Mass.gram * Flour).to(Volume.cup)
1.4881 cup Flour
>>> (1 * Volume.cup * Sugar).to(Mass.gram)
288 g Sugar
>>> (175 * Mass.gram * Flour).to(Volume.tablespoon)
16.6667 tbsp. Flour
>>> (1 * Volume.teaspoon * Salt).to(Mass.gram)
6 g Salt
>>> (1 * Mass.stick * Butter).to(Mass.gram)
113.398 g Butter
>>> (125 * Mass.gram * Butter).to(Mass.stick)
1.10231 stick Butter
>>> (37.7 * Temperature.celsius).to(Temperature.fahrenheit)
99.86 °F
>>> (210 * Temperature.celsius).to(Temperature.thermostat)
thermostat 7
>>> (Temperature.thermostat * 6).to(Temperature.fahrenheit)
356 °F
"""

# python 2 compatibility
from __future__ import division
from builtins import int, str


class Element(object):
    """Food or other element with certain properties"""

    def __init__(self, name, **properties):
        """properties are set as attributes for easier access

        >>> Element('flour', color='#ffffff', density=0.7).density
        0.7
        """
        self.name = name
        for prop in properties:
            setattr(self, prop, properties[prop])

    def __repr__(self):
        return self.name


class Ingredient(object):
    """An amount of a certain element

    >>> Ingredient(3 * Volume.teaspoon, Element('sugar'))
    3 tsp. sugar

    shorter syntax using multiplication:
    >>> 30 * Volume.milliliter * Element('cyanide')
    30 ml cyanide
    """

    def __init__(self, amount, element):
        self.amount = amount
        self.element = element

    def to(self, unit):
        """Convert to a different unit, or measure depending on the properties of its element

        >>> (2 * Volume.cup * Element('water')).to(Volume.milliliter)
        480 ml water
        >>> (1 * Volume.cup * Flour).to(Mass.gram).amount
        168 g
        """
        if isinstance(unit, Measure):
            unit = unit.baseUnit
        if unit.measure == self.amount.unit.measure:
            return Ingredient(self.amount.to(unit), self.element)
        return self._transform(unit)

    def __repr__(self):
        return "%s %s" % (self.amount, self.element)

    def _transform(self, unit):
        newAmount = self.amount.unit.measure.transformTo(unit.measure)(
            self.amount, self.element
        )
        return Ingredient(newAmount.to(unit), self.element)


class Amount(object):
    """Amount/quantity of a Unit

    >>> Amount(5, Mass.decigram)
    5 dg
    >>> 3 * Volume.hectoliter
    3 hl
    """

    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def to(self, unit, properties=None):
        """convert to another unit of the same measure

        >>> (2 * Volume.liter).to(Volume.centiliter)
        200 cl
        >>> (0 * Temperature.kelvin).to(Temperature.celsius)
        -273.15 °C
        """
        if not isinstance(unit, Unit):
            raise TypeError(
                "Expected Unit type but unit is type " + type(unit).__name__
            )
        if self.unit == unit:
            return self
        if unit.measure != self.unit.measure:
            raise TypeError(
                "Can't implicitely convert from "
                + self.unit.measure.name
                + " to "
                + unit.measure.name
            )
        baseAmount = self
        if self.unit != self.unit.measure.baseUnit:
            baseAmount = self.toBaseUnit()
        if unit == baseAmount.unit:
            return baseAmount
        newAmount = Amount(unit.converter.fromBase(baseAmount.value), unit)
        return newAmount

    def toBaseUnit(self):
        """convert to the base unit of a unit measure"""
        return self.unit.converter.toBase(self.value) * self.unit.measure.baseUnit

    def __mul__(self, other):
        """Ingredient constructor or simple numeric multiplier

        >>> 42 * Mass.gram * Flour
        42 g Flour
        >>> 3 * Amount(5, Volume.liter)
        15 l
        """
        if isinstance(other, Element):
            return Ingredient(self, other)
        if isinstance(other, (int, float)):
            return Amount(self.value * other, self.unit)
        raise TypeError(
            "Unable to multiply " + self.unit.measure + " and " + type(other).__name__
        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        """regular division

        >>> Amount(42, Mass.gram) / 7
        6 g
        """
        if isinstance(other, (int, float)):
            return Amount(self.value / other, self.unit)
        raise TypeError(
            "Unable to divide " + self.unit.measure + " by " + type(other).__name__
        )

    def __repr__(self):
        valuestr = "%g" % self.value
        return "%s %s" % (
            (self.unit.abrev, valuestr)
            if self.unit.preFix
            else (valuestr, self.unit.abrev)
        )


class Measure(object):
    """Category of units (mass, length, volume, ...)
    Defined by a base unit (i.e. gram)
    several units can be bound (added) to a measure
    >>>
    """

    def __init__(self, name, baseUnit):
        """Create a new measure defined by a base unit

        >>> Measure('time', Unit('second', 's')).name
        'time'
        """
        self.name = name
        self.units = {}
        self.addUnit(baseUnit)
        self.baseUnit = baseUnit
        self.transform_functions = {}

    def addUnit(self, unit):
        """add a Unit to a measure
        unit is then accessible as an attribute

        >>> Time.addUnit(Unit('day', 'day')); Time.day
        day
        """
        if not isinstance(unit, Unit):
            raise TypeError("Expected a type Unit, but got type " + type(unit).__name__)
        if unit.name in self.units:
            raise ValueError(
                "%s already contains a unit named %s" % (self.name, unit.name)
            )
        unit.measure = self
        self.units[unit.name] = unit
        for name in unit.alternate_names:
            self.units[name] = unit
        setattr(self, unit.name, unit)

    def addUnits(self, units):
        """add a collection of units
        see addUnit

        >>> Volume.addUnits([Unit('drop', 'drop'), Unit('bowl', 'bowl')]); Volume.drop
        drop
        """
        for unit in units:
            self.addUnit(unit)

    def transformTo(self, measure):
        """get a registered transformation function to a different Measure"""
        if measure not in self.transform_functions:
            raise ValueError(
                "No transformation known bewteen " + self.name + " and " + measure.name
            )
        return self.transform_functions[measure]

    def addTransform(self, toMeasure, function):
        """Register a transformation function to another Measure"""
        if toMeasure not in self.transform_functions:
            self.transform_functions[toMeasure] = function


class Converter(object):
    """set of methods to convert a unit to and from a base unit
    easily created through some helper constructor fonctions below

    >>> Converter(lambda n: n / 2, lambda n: 2 * n).toBase(50)
    25.0
    """

    def __init__(self, toBaseConversion, fromBaseConversion):
        """create a converter using 2 functions : convert to base, convert from base"""
        self.toBase = toBaseConversion
        self.fromBase = fromBaseConversion

    @property
    def reverse(self):
        """return a converter with swapped conversion functions

        >>> Converter(lambda n: n / 2, lambda n: 2 * n).reverse.toBase(21)
        42
        """
        return Converter(self.fromBase, self.toBase)

    @classmethod
    def Linear(cls, factor, constant=0):
        """linear function converter (y = ax + b, x = (y - b) / a)

        >>> Converter.Linear(5, 1).toBase(2)
        11
        """
        return cls(lambda n: n * factor + constant, lambda n: (n - constant) / factor)

    @classmethod
    def Constant(cls, constant):
        """converter that adds a constant (y = x + a, x = y - a)

        >>> Converter.Constant(7).toBase(5)
        12
        """
        return cls.Linear(1, constant)


Converter.Neutral = Converter.Linear(1)
""" Converter that doesn't change the value
"""


class Unit(object):
    """Unit of a measure, i.e. gram (mass), liter (volume) etc."""

    def __init__(
        self,
        name="Unknown unit",
        abrev="?unit",
        preFix=False,
        converter=Converter.Neutral,
        alternate_names=[],
    ):
        """create a unit by name

        parameters:
        name: name of the unit ('liter', 'second', 'joule')
        abrev: abreviated name of the unit, used for displaying ('l', 's', 'J')
        prefix: for display purposes: if true, the unit name precedes the number (i.e. '$ 5')
        converter: a Converter object to convert this unit to and from the base unit

        >>> Length.addUnit(Unit('yard', 'yd', converter=Converter.Linear(0.9144)))
        >>> (3 * Length.decameter).to(Length.yard)
        32.8084 yd
        """
        self.name = name
        self.abrev = abrev
        self.preFix = preFix
        self.converter = converter
        self.measure = None  # set by Measures when they add a unit
        self.alternate_names = alternate_names

    def __mul__(self, other):
        return self.__rmul__(other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Amount(other, self)

    def __repr__(self):
        return self.name


def SIUnitsFromUnit(unit):
    """list the most common SI units based of a base unit
    result does NOT include the base unit
    prefixes: milli, centi, deci, deca, hecto, kilo

    >>> list(SIUnitsFromUnit(Unit('liter', 'l')))
    [milliliter, centiliter, deciliter, decaliter, hectoliter, kiloliter]
    """
    if not isinstance(unit, Unit):
        raise TypeError("Expected type Unit, but unit is type " + type(unit).__name__)
    return map(
        lambda t: Unit(
            t[0] + unit.name,
            t[1] + unit.abrev,
            converter=Converter.Linear(t[2]),
            preFix=unit.preFix,
        ),
        [
            ("milli", "m", 0.001),
            ("centi", "c", 0.01),
            ("deci", "d", 0.1),
            ("deca", "da", 10),
            ("hecto", "h", 100),
            ("kilo", "k", 1000),
        ],
    )


# Common cooking measures

Mass = Measure("Mass", Unit("gram", "g"))
Mass.addUnits(SIUnitsFromUnit(Mass.gram))

Volume = Measure("Volume", Unit("liter", "l"))
Volume.addUnits(SIUnitsFromUnit(Volume.liter))

Temperature = Measure("Temperature", Unit("celsius", "°C"))
Temperature.addUnits(
    [
        Unit("kelvin", "°K", converter=Converter.Constant(-273.15)),
        Unit("fahrenheit", "°F", converter=Converter.Linear(1.8, 32).reverse),
        Unit("thermostat", "thermostat", converter=Converter.Linear(30), preFix=True),
    ]
)

# other measures

Length = Measure("Length", Unit("meter", "m"))
Length.addUnits(SIUnitsFromUnit(Length.meter))

Time = Measure("Time", Unit("second", "s"))
Time.addUnits(
    [
        Unit("minute", "min", converter=Converter.Linear(60)),
        Unit("hour", "h", converter=Converter.Linear(3600)),
    ]
)

Count = Measure("Count", Unit("unit", ""))
Count.addUnits([Unit("dozen", "doz", converter=Converter.Linear(12))])
# measure conversion

milliliter = Volume.milliliter
gram = Mass.gram

Volume.addTransform(
    Mass, lambda volume, element: (element.density * volume.to(milliliter)).value * gram
)
Mass.addTransform(
    Volume, lambda mass, element: ((mass.to(gram)).value / element.density) * milliliter
)

# USA cooking units

CUP_IN_LITER = 0.236588  # 'US legal' cup definition
GALLON_IN_LITER = 0.231 * 2.54**3  # 231 cubic inches
POUND_IN_GRAMS = 453.59237  # NIST pound definition

Volume.addUnits(
    [
        # FDA units
        Unit(
            "pinch",
            "pinch",
            converter=Converter.Linear(CUP_IN_LITER / 768),
            alternate_names=["pinches"],
        ),
        Unit(
            "teaspoon",
            "tsp.",
            converter=Converter.Linear(CUP_IN_LITER / 48),
            alternate_names=["teaspoons"],
        ),
        Unit(
            "tablespoon",
            "tbsp.",
            converter=Converter.Linear(CUP_IN_LITER / 16),
            alternate_names=["tablespoons"],
        ),
        Unit(
            "fluidOunce",
            "fl. oz.",
            converter=Converter.Linear(CUP_IN_LITER / 8),
            alternate_names=["fluidOunces", "fluid ounce", "fluid ounces"],
        ),
        Unit(
            "cup",
            "cup",
            converter=Converter.Linear(CUP_IN_LITER),
            alternate_names=["cups"],
        ),
        # other units
        Unit(
            "pint",
            "pt.",
            converter=Converter.Linear(GALLON_IN_LITER / 8),
            alternate_names=["pints"],
        ),
        Unit(
            "quart",
            "qt",
            converter=Converter.Linear(GALLON_IN_LITER / 4),
            alternate_names=["quarts"],
        ),
        Unit(
            "gallon",
            "gal.",
            converter=Converter.Linear(GALLON_IN_LITER),
            alternate_names=["gallons"],
        ),
        Unit("bunch", "bunch", alternate_names=["sticks"]),
    ]
)

Mass.addUnits(
    [
        Unit(
            "ounce",
            "oz",
            converter=Converter.Linear(POUND_IN_GRAMS / 16),
            alternate_names=["ounces"],
        ),
        # Unit('stick',   'stick',    converter=Converter.Linear(POUND_IN_GRAMS / 4), alternate_names=['sticks']),
        Unit("stick", "stick", alternate_names=["sticks"]),
        Unit(
            "pound",
            "lb",
            converter=Converter.Linear(POUND_IN_GRAMS),
            alternate_names=["pounds"],
        ),
        Unit("head", "head", alternate_names=["heads"]),
        Unit("clove", "clove", alternate_names=["cloves"]),
    ]
)


# Common Ingredients

Flour = Element("Flour", density=0.7)
Sugar = Element("Sugar", density=1.2)
Salt = Element("Salt", density=1.2)
Butter = Element("Butter", density=0.9)

available_measures = dict(Volume.units, **Mass.units, **Count.units)
available_measures.update(Mass.units)
available_measures.update(Count.units)


# run the module to make it test itself
if __name__ == "__main__":
    import doctest

    doctest.testmod()
