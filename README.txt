The biosim package contains a flask application that handles http requests for climate variables and pest development stages.
The application is developed by Mathieu Fortin, Canadian Wood Fibre Centre, and Rémi Saint-Amant, Laurentian Forestry Centre.
More information is available at https://sourceforge.net/p/mrnfforesttools/biosimclient/wiki/MainPage/

The Python wheel file is a light package: it does not contain the weather files, the DEM and the layers. All these files must be downloaded separately 
and put in different subfolders of biosim/data.

The application is licensed under the LGPL-3.0.

Copyright 2020 Her Majesty the Queen in right of Canada.

Maintainer: Mathieu Fortin (mathieu.fortin.re@gmail.com)
Bug report: https://sourceforge.net/p/mrnfforesttools/biosimclient/tickets/