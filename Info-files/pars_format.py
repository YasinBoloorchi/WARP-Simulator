Instructions = [
    
                [('release', 'release (F0,BA)')], 
                
                [('pull', 'pull (F0, #0)')],
                
                [('sleep', 'sleep')],
                
                [('release', 'release (F0,AC)'),
                 ('if', 'if !has(F0,BA) then pull (F0,#1,BA) else pull(F0,#1,AC)')],
                
                [('pull', 'pull (F1, #2)')]
                
                ]
