
from configs import *


import pytest


class TestGraphicsInitialization:

    def test_graphics(self):

        from blocks.engine.oriented import AcyclicGraphic

        graphic = AcyclicGraphic()
        assert isinstance(graphic, AcyclicGraphic)

    def test_graphics_links(self):

        from blocks.engine.oriented import AcyclicGraphic

        link = [ ('g',2),(4,1),(0,'g'),
                (2,4),(2,54),(3,4),(7,54),
                ('g',3),(54,8),(3,8) ]

        graphic = AcyclicGraphic(links=link, first=0, last=None)
        
        assert len(graphic.nodes) == 9


    def test_graphics_iteration(self):

        from blocks.engine.oriented import AcyclicGraphic

        link = [ ('g',2),(4,1),(0,'g'),
                (2,4),(2,54),(3,4),(7,54),
                ('g',3),(54,8),(3,8) ]

        graphic = AcyclicGraphic(links=link, first=0, last=None)
        nodes = list(graphic)

        assert len(graphic.nodes) == 9


        graphic.build()

        for g in graphic:
            g.resolve()


    def test_graphics_cycle(self):

        from blocks.engine.oriented import CyclicGraphic

        link = [ ('g',2),(4,1),(0,'g'),
                (2,4),(2,54),(3,4),(7,54),
                ('g',3),(54,8),(3,8) ]

        graphic = CyclicGraphic(links=link, first=0, last=None)
        
        assert len(graphic.nodes) == 9
            
    def test_graphics_cycle_iteration(self):

        from blocks.engine.oriented import CyclicGraphic

        link = [ ('g',2),(4,1),(0,'g'),
                (2,4),(2,54),(3,4),(7,54),
                ('g',3),(54,8),(3,8) ]

        graphic = CyclicGraphic(links=link, first=0, last=None)
        nodes = list(graphic)

        assert len(graphic.nodes) == 9


        graphic.build()

        for g in graphic:
            g.resolve()
    
    def test_graphics_cycle_condition(self):

        from blocks.engine.oriented import CyclicGraphic

        link = [ ('g',2),(4,1),(0,'g'),
                (2,4),(2,54),(3,4),(7,54),
                ('g',3),(54,8),(3,8) ]

        graphic = CyclicGraphic(links=link, first=0, last=None)
        nodes = list(graphic)

        assert len(graphic.nodes) == 9

        def eq(key_attr='n', value='n'):
            if key_attr==value:
                return False
            return True
        
        graphic.add_condition(
            start=[8],
            default=96,
            end=[45,96],
            ctype='IF',
            method=eq,
            switch={
                45:True,
                96:False
            }    
        )

        graphic.build()

        for g in graphic:
            g.resolve()

    def test_graphics_cycle_loop(self):

        from blocks.engine.oriented import CyclicGraphic

        link = [ ('g',2),(4,1),(0,'g'),
                (2,4),(2,54),(3,4),
                ('g',3),(54,8),(3,8), 
                (96,52) ]

        graphic = CyclicGraphic(links=link, first=0, last=None)
        nodes = list(graphic)

        assert len(graphic.nodes) == 10

        graphic.add_loop(
            start=[2],
            end=[8],
            epoch=3,
            ctype='FOR',
        )

        graphic.build()

        for g in graphic:
            g.resolve()











