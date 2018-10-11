var FOLLOWED_IDS = new Set();

Board = function(target_element_id){
    var self = {};
    self._moves = [];
    self._current_move_index=0;
    self._followedId = 0;

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

    self.players = function(p1,p2){
        var p1Label=self._getPlayerLabel("p1");
        var p2Label=self._getPlayerLabel("p2");

        $(p1Label).text(p1);
        $(p2Label).text(p2);
    }

    self.follow = function(){
        self._choose_board();
    }

    self._clear = function(){
        for(var moveId in self._moves){
            var move=self._moves[moveId];
            var x=move[0];
            var y=move[1];
            var cell=document.getElementById(self._cell_id(x,y));
            cell.className="";
        }

        self._moves=[]
        self._current_move_index=0;
        self.players("","");
    }

    self._choose_board = function(response=null){
        var selectedBoard = self._select_board(response);

        if(response!=null){
            if(selectedBoard!=null){
                self._clear();

                FOLLOWED_IDS.delete(self._followedId);
                self._followedId=selectedBoard["_id"];

                FOLLOWED_IDS.add(self._followedId);

                self.players(selectedBoard["player1"],selectedBoard["player2"]);
                self._follow_update(selectedBoard);
            }else{
                setTimeout(self._choose_board, 1000);
            }

            return;
        }

        $.ajax({
            method: "GET",
            url: "/live_board",
            dataType: "json",
            data: {}
        }).done(self._choose_board).error(function(){
            self._choose_board({});
        });
    }

    self._select_board = function(response){
        if(response==null || !("boards" in response))
            return null;

        var moveCount=1000;
        var selectedBoard=null;
        var boards=response["boards"];
        for(var id in boards){
            var board=boards[id];
            if(FOLLOWED_IDS.has(board["_id"]))
                continue;

            if(board["moves"].length<moveCount){
                moveCount=board["moves"].length;
                selectedBoard=board;
            }
        }
        return selectedBoard;
    }

    self._follow_update = function(response){
        if("finished_board" in response){
            self.loadMoves(response["finished_board"]["moves"].slice(self._moves.length));
            setTimeout(self._choose_board, 5000);
            return;
        }

        if("moves" in response){
            self.loadMoves(response["moves"]);
        }

        $.ajax({
            method: "GET",
            url: "/live_board",
            dataType: "json",
            data: { id: self._followedId, move: self._moves.length}
        }).done(self._follow_update).error(self._choose_board);
    }

    self._getPlayerLabel = function(tag){
        var labelId=target_element_id +"-"+tag;
        var pEl=document.getElementById(labelId);
        if(!pEl){
            pEl=document.createElement('div');
            pEl.id=labelId;
            pEl.className=tag;
            document.getElementById(target_element_id).appendChild(pEl);
        }
        return pEl;
    }


    self._create();
    return self;
}