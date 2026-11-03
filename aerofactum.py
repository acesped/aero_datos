Run set -euo pipefail
Instagram verificado: @aerofactum
Traceback (most recent call last):
  File "/home/runner/work/aero_datos/aero_datos/aerofactum.py", line 814, in <module>
    if __name__=='__main__':sys.exit(main())
                                     ^^^^^^
  File "/home/runner/work/aero_datos/aero_datos/aerofactum.py", line 794, in main
    ep=select_episode(episodes,gh,args.episode or None)
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/aero_datos/aero_datos/aerofactum.py", line 369, in select_episode
    state,_=load_state(gh) if gh else ({'episodes':{}},None)
            ^^^^^^^^^^^^^^
  File "/home/runner/work/aero_datos/aero_datos/aerofactum.py", line 357, in load_state
    raw,sha=gh.read(STATE_PATH)
            ^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/aero_datos/aero_datos/aerofactum.py", line 343, in read
    if r.status_code>=400:raise RuntimeError(f'Lectura GitHub HTTP {r.status_code}')
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Lectura GitHub HTTP 500
Error: Process completed with exit code 1.
