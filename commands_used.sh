
# THIS IS developed under bentoml version 1.0.21, a mordern version is full of bug!


# start up bento service, locally to test service.py
# bentoml serve src.service8:svc

# after having bentofile.yaml
# build BENTO
bentoml build
# the output will look sth. like:
# $ bentoml build
# Building BentoML service "admissions_service:jfkazle7qge6gaav" from build context "/mnt/d/DataScienceTraining/bentoML-exam/examen_bentoml".
# Packing model "admissions_model_with_scaler:mo33gdu7pke6gaav"
# Locking PyPI package versions.
# WARNING: --strip-extras is becoming the default in version 8.0.0. To silence this warning, either use --strip-extras to opt into the new default or use --no-strip-extras to retain the existing behavior.

# ██████╗░███████╗███╗░░██╗████████╗░█████╗░███╗░░░███╗██╗░░░░░
# ██╔══██╗██╔════╝████╗░██║╚══██╔══╝██╔══██╗████╗░████║██║░░░░░
# ██████╦╝█████╗░░██╔██╗██║░░░██║░░░██║░░██║██╔████╔██║██║░░░░░
# ██╔══██╗██╔══╝░░██║╚████║░░░██║░░░██║░░██║██║╚██╔╝██║██║░░░░░
# ██████╦╝███████╗██║░╚███║░░░██║░░░╚█████╔╝██║░╚═╝░██║███████╗
# ╚═════╝░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░░╚════╝░╚═╝░░░░░╚═╝╚══════╝

# Successfully built Bento(tag="admissions_service:jfkazle7qge6gaav").

# Possible next steps:

 # * Containerize your Bento with `bentoml containerize`:
    # $ bentoml containerize admissions_service:jfkazle7qge6gaav

 # * Push to BentoCloud with `bentoml push`:
    # $ bentoml push admissions_service:jfkazle7qge6gaav



# VERY important: u have to add "name" and "version" field to the bento.yml, otherwise docker containerize will complain!
# the "name"(bento-exam) and "version"(v0) will serve as the docker image name and version, you will see that in the Docker Desktop 
# vi ~/bentoml/bentos/admissions_service/jfkazle7qge6gaav/bento.yaml


# NOW:
# containerize bento
bentoml containerize admissions_service:jfkazle7qge6gaav

 # 1 warning found (use docker --debug to expand):
 # - FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 6)
# Successfully built Bento container for "admissions_service:jfkazle7qge6gaav" with tag(s) "bento-exam:v0"
# To run your newly built Bento container, run:
    # docker run -it --rm -p 3000:3000 bento-exam:v0 serve
	

# run the Containerizem, watch on:  http://localhost:3001
docker run -p 3000:3000 bento-exam:v0

# save the image
docker save -o adili_bento-exam.tar bento-exam:v0




# Unit test, when runnig the test, keep container or "bentoml serve" running, so that localhost:3000 is available to test
 pytest -v test_service5.py












