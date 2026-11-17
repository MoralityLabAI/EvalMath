"""Exact sparse identifiability from public GF(2) observations, size bounded.

Every weight-w support splits into disjoint floor(w/2) and ceil(w/2) halves.
Hash the XOR observation signatures of all left halves, then exhaust matching
complements for every right half. Two distinct solutions prove ambiguity;
one after exhaustive lookup proves uniqueness in the stated weight-w family.
No hidden goal, supplied answer or neural output is used by the decoder.
The explicit half-enumeration cap makes larger unavailable domains visible.
"""
from __future__ import annotations
from itertools import combinations
from math import comb


def decode(dimension, goal_rank, transcript, width=6, max_half_terms=1_000_000):
    if type(dimension) is not int or dimension < 1 or type(goal_rank) is not int or goal_rank < 1:
        raise ValueError('positive dimension and rank required')
    if type(width) is not int or not 0 <= width <= dimension:
        raise ValueError('invalid exact support width')
    if type(max_half_terms) is not int or max_half_terms < 1:
        raise ValueError('positive enumeration cap required')
    left_size=width//2
    right_size=width-left_size
    left_terms,right_terms=comb(dimension,left_size),comb(dimension,right_size)
    base={'method':'exact_sparse_GF2_meet_in_middle', 'dimension':dimension,
          'goal_rank':goal_rank,'known_width':width,'equations':len(transcript),
          'single_output_goal_family_size':comb(dimension,width),
          'left_half_terms':left_terms,'right_half_terms':right_terms,
          'max_half_terms':max_half_terms,
          'family':'Each output has exact known weight; no additional disjointness assumption.'}
    if left_terms+right_terms>max_half_terms:
        return {**base,'status':'unavailable_enumeration_cap','outputs':[]}
    columns=[0]*dimension
    targets=[0]*goal_rank
    for q,(mask,response) in enumerate(transcript):
        if type(mask) is not int or mask<0 or mask>>dimension:
            raise ValueError('invalid public query')
        if len(response)!=goal_rank or any(type(b) is not int or b not in (0,1) for b in response):
            raise ValueError('invalid public response')
        for i in range(dimension):
            if mask>>i&1:columns[i]|=1<<q
        for j,b in enumerate(response):targets[j]|=b<<q

    def halves(size):
        for indices in combinations(range(dimension),size):
            signature,mask=0,0
            for i in indices:
                signature^=columns[i]
                mask|=1<<i
            yield signature,mask

    table={}
    for signature,mask in halves(left_size):table.setdefault(signature,[]).append(mask)
    outputs=[]
    for j,target in enumerate(targets):
        solutions=set()
        checked=0
        exhaustive=True
        if left_size==right_size:
            right_groups=table.items()
        else:
            right_table={}
            for signature,mask in halves(right_size):right_table.setdefault(signature,[]).append(mask)
            right_groups=right_table.items()
        for right_signature,rights in right_groups:
            lefts=table.get(target^right_signature,())
            if not lefts:continue
            for left in lefts:
                for right in rights:
                    checked+=1
                    if left&right:continue
                    support=left|right
                    if support.bit_count()!=width:raise AssertionError('half partition count')
                    if any((mask&support).bit_count()%2!=response[j] for mask,response in transcript):
                        raise AssertionError('independent candidate equation check')
                    solutions.add(support)
                    if len(solutions)==2:break
                if len(solutions)==2:break
            if len(solutions)==2:
                exhaustive=False
                break
        status='ambiguous_at_least_two' if len(solutions)==2 else 'unique' if len(solutions)==1 else 'inconsistent'
        outputs.append({'output_index':j,'status':status,'lookup_exhausted':exhaustive,
                        'compatible_support_count_capped_at_two':len(solutions),
                        'matching_half_pairs_checked':checked,
                        'witness_supports':[[i for i in range(dimension) if m>>i&1] for m in sorted(solutions)]})
    status='unique' if all(o['status']=='unique' for o in outputs) else (
        'inconsistent' if any(o['status']=='inconsistent' for o in outputs) else 'ambiguous_at_least_two')
    return {**base,'status':status,'outputs':outputs}


def first_unique_prefix(dimension, goal_rank, transcript, width=6, max_half_terms=1_000_000, final=None):
    final=final or decode(dimension,goal_rank,transcript,width,max_half_terms)
    if final['status']!='unique':return None
    low,high=0,len(transcript)
    while low<high:
        middle=(low+high)//2
        if decode(dimension,goal_rank,transcript[:middle],width,max_half_terms)['status']=='unique':high=middle
        else:low=middle+1
    return low
