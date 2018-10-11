Board = function(target_element_id){
    self = {};
    self._moves = [];
    self._current_move_index=0;

    self._cell_id = function(x,y){
        return target_element_id+"-"+String(x)+"-"+String(y);
    }

    self._create = function(){
        var el=document.getElementById(target_element_id);
        for(var y=0;y<15;++y){
            var row=document.createElement('div');
            row.className="board_row";
            el.appendChild(row);
            for(var x=0;x<15;++x){
                var cellWrapper=document.createElement('div');
                cellWrapper.className="board_cell_wrapper";

                var cell=document.createElement('div');
                cell.id = self._cell_id(x,y);
                cell.className="board_cell";

                cellWrapper.appendChild(cell);
                row.appendChild(cellWrapper);
            }
        }
    }

    self._gotoMove = function(moveIndex){

        if(moveIndex<0)
            moveIndex=0;

        if(moveIndex>=self._moves.length)
            moveIndex=self._moves.length-1;

        var replayDirection=Math.sign(moveIndex-self._current_move_index);

        while(true){

            if(replayDirection>=0){
                self._current_move_index+=replayDirection;
            }

            var move=self._moves[self._current_move_index];
            var x=move[0];
            var y=move[1];
            var cell=document.getElementById(self._cell_id(x,y));

            if(replayDirection>=0){
                cell.className=self._current_move_index % 2 == 0 ? 'board_cell_cross' : 'board_cell_circle';
            }else{
                cell.className="";
            }

            if(replayDirection<0){
                self._current_move_index+=replayDirection;
            }

            if(self._current_move_index==moveIndex)
                break;
        }
    }

    self.firstMove = function(){
        self._gotoMove(0);
    }

    self.lastMove = function(){
        self._gotoMove(self._moves.length);
    }

    self.previousMove = function(){
        self._gotoMove(self._current_move_index-1);
    }

    self.nextMove = function(){
        self._gotoMove(self._current_move_index+1);
    }

    self.move = function(x,y){
        self._moves.push([x,y]);
        self.lastMove()
    }

    self.loadMoves = function(moves){
        for(move_id in moves){
            move=moves[move_id];
            self.move(move[0],move[1]);
        }
    }

    self._create();
    return self;
}