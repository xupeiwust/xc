//----------------------------------------------------------------------------
//  biblioteca vtk_aux; utilidades construidas sobre VTK (<http://www.vtk.org>)
//
//  Copyright (C)  Luis C. Pérez Tato
//
//  XC utils is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or 
//  (at your option) any later version.
//
//  This software is distributed in the hope that it will be useful, but 
//  WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.  
//
// You should have received a copy of the GNU General Public License 
// along with this program.
// If not, see <http://www.gnu.org/licenses/>.
//----------------------------------------------------------------------------
//vtkDoubleHeadedArrowSource.h

// .NAME vtkDoubleHeadedArrowSource - Appends a cylinder to a cone to form an arrow.
// .SECTION Description
// vtkDoubleHeadedArrowSource was intended to be used as the source for a glyph.
// The shaft base is always at (0,0,0). The arrow tip is always at (1,0,0).
// The resolution of the cone and shaft can be set and default to 6.
// The radius of the cone and shaft can be set and default to 0.03 and 0.1.
// The length of the tip can also be set, and defaults to 0.35.


#ifndef __vtkDoubleHeadedArrowSource_h
#define __vtkDoubleHeadedArrowSource_h

#include "vtkPolyDataAlgorithm.h"

class VTK_GRAPHICS_EXPORT vtkDoubleHeadedArrowSource : public vtkPolyDataAlgorithm
{
public:
  // Description
  // Construct cone with angle of 45 degrees.
  static vtkDoubleHeadedArrowSource *New();

  vtkTypeRevisionMacro(vtkDoubleHeadedArrowSource,vtkPolyDataAlgorithm);
  void PrintSelf(ostream& os, vtkIndent indent);
    
  // Description:
  // Set the length, and radius of the tip.  They default to 0.35 and 0.1
  vtkSetClampMacro(TipLength,double,0.0,1.0);
  vtkGetMacro(TipLength,double);
  vtkSetClampMacro(TipRadius,double,0.0,10.0);
  vtkGetMacro(TipRadius,double);
  
  // Description:
  // Set the resolution of the tip.  The tip behaves the same as a cone.
  // Resoultion 1 gives a single triangle, 2 gives two crossed triangles.
  vtkSetClampMacro(TipResolution,int,1,128);
  vtkGetMacro(TipResolution,int);

  // Description:
  // Set the radius of the shaft.  Defaults to 0.03.
  vtkSetClampMacro(ShaftRadius,double,0.0,5.0);
  vtkGetMacro(ShaftRadius,double);

  // Description:
  // Set the resolution of the shaft.  2 gives a rectangle.
  // I would like to extend the cone to produce a line,
  // but this is not an option now.
  vtkSetClampMacro(ShaftResolution,int,0,128);
  vtkGetMacro(ShaftResolution,int);

protected:
  vtkDoubleHeadedArrowSource();
  ~vtkDoubleHeadedArrowSource() {};

  int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);

  int TipResolution;
  double TipLength;
  double TipRadius;

  int ShaftResolution;
  double ShaftRadius;

private:
  vtkDoubleHeadedArrowSource(const vtkDoubleHeadedArrowSource&); // Not implemented.
  void operator=(const vtkDoubleHeadedArrowSource&); // Not implemented.
};

#endif


