"""Command line interface."""

import os
try:
    from ConfigParser import ConfigParser
except ImportError:
    # Python 3.x
    from configparser import ConfigParser

import alembic.config
import alembic.context
from sqlalchemy.engine.url import URL
import click
from humilis.environment import Environment
import shutil

from polku_poc.settings import config, PROJECT_PATH

# Python 2.x compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


@click.group(name="polkupoc")
@click.option("--envpath", default=config.ENVIRONMENT_PATH,
              type=click.Path(exists=True, resolve_path=True),
              help="Path to the humilis environment definition file")
@click.option("--stage", default=config.STAGE, help="Deployment stage name")
@click.option("--parameters", default=config.ENVIRONMENT_PARAMS_PATH,
              type=click.Path(exists=True, resolve_path=True),
              help="Path to the deployment parameters file")
@click.pass_context
def main(ctx, envpath, stage, parameters):
    """Polku sample app: deployment CLI."""
    ctx.obj = {"env": Environment(envpath, stage=stage, parameters=parameters)}
    config.context = ctx.obj


@main.command()
@click.option('--output', help="Store environment outputs in this file",
              metavar="FILE", default=config.ENVIRONMENT_OUTPUTS_PATH)
@click.option('--update/--no-update', help="Update already deployed layers",
              default=False)
@click.pass_context
def apply(ctx, output, update):
    """Create or update the environment."""
    env = ctx.obj["env"]
    output_file = output.format(environment=env.name, stage=env.stage)
    print("==> Deploying infrastructure to AWS ...")
    env.create(output_file=output_file, update=update)
    print("==> Done deploying infrastructure to AWS.")


@main.command()
@click.option("--ask/--no-ask", default=True)
@click.pass_context
def destroy(ctx, ask):
    """Destroy the deployed environment."""
    env = ctx.obj["env"]
    print("==> Destroying deployment for stage '{}' ...".format(env.stage))
    if ask:
        confirmation = input("Are you sure (y/n)? ")
    else:
        confirmation = "y"

    if confirmation == "y":
        try:
            bucket = env.outputs.get("s3", {}).get("BucketName")
            if bucket:
                _empty_bucket(bucket)
        except FileNotFoundError:
            pass
        try:
            env.delete()
        except AwsError:
            # Some files may have arrived to the bucket after emptying it
            _empty_bucket(bucket)
            env.delete()
    else:
        print("Cancelled!")


def _empty_bucket(bucket):
    """Empty the bucket associated to a deployment."""
    print("Emptying bucket {} ...".format(bucket))
    os.system("aws s3 rm s3://{} --recursive".format(bucket))
    print("Bucket {} has been emptied".format(bucket))


@main.command(name="alembic")
@click.pass_context
@click.argument("args", nargs=-1)
def polkupoc_alembic(ctx, args):
    """Migrate Redshift with Alembic."""

    alembic.context.sqlalchemy_url = str(URL(
        host=os.environ["REDSHIFT_HOST"],
        port=os.environ["REDSHIFT_PORT"],
        database=os.environ["REDSHIFT_DB"],
        username=os.environ["REDSHIFT_USER"],
        password=os.environ["REDSHIFT_PWD"],
        drivername="redshift+psycopg2"))
    config_file = _make_stage_dir(ctx.obj["env"].stage.lower())
    args = ["-c", config_file] + list(args)
    alembic.config.main(prog="polkupoc alembic", argv=args)


def _make_stage_dir(stage):
    """Create a separate Alembic dir for each stage."""
    dirname = os.path.join(PROJECT_PATH, "migrations", "stages", stage)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
        os.makedirs(os.path.join(dirname, "versions"))

    _make_env_file(dirname)
    _make_mako_file(dirname)
    return _make_alembic_config(stage)



def _make_env_file(targetdir):
    """Create Alembic's env.py file for a stage."""
    envfile = os.path.join(targetdir, "env.py")
    envfile_template = os.path.join(PROJECT_PATH, "migrations", "env.py")
    if not os.path.isfile(envfile):
        shutil.copyfile(envfile_template, envfile)


def _make_mako_file(targetdir):
    """Create Alembic's script.py.mako for a stage."""
    mako = os.path.join(targetdir, "script.py.mako")
    mako_template = os.path.join(PROJECT_PATH, "migrations", "script.py.mako")
    if not os.path.isfile(mako):
        shutil.copyfile(mako_template, mako)


def _make_alembic_config(stage):
    """Make alembic.ini for a stage."""
    parser = ConfigParser()
    parser.read(os.path.join(PROJECT_PATH, "alembic.ini"))
    script_location = parser.get("alembic", "script_location")
    script_location = os.path.relpath(
        os.path.join(PROJECT_PATH, script_location, "stages", stage),
        PROJECT_PATH)
    parser.set("alembic", "script_location", script_location)
    config_file = os.path.join(
        PROJECT_PATH, "migrations", "stages", stage, "alembic.ini")
    with open(config_file, "w") as f:
        parser.write(f)
    return config_file
